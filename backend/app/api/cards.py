from app.models.models import Transaction
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from datetime import datetime
from ..core.database import get_db
from ..models import models, schemas

router = APIRouter()

@router.post("/cards/", response_model=schemas.Card)
def create_card(card: schemas.CardCreate, db: Session = Depends(get_db)):
    db_card = models.Card(
        name=card.name, 
        last_4_digits=card.last_4_digits,
        bank=card.bank
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@router.get("/cards/", response_model=List[schemas.Card])
def read_cards(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cards = db.query(models.Card).offset(skip).limit(limit).all()
    return cards

@router.post("/cards/{card_id}/upload-statement/")
def upload_statement(
    card_id: int, 
    files: List[UploadFile] = File(...), 
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Verify card exists
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Save files and process
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    total_processed = 0
    processed_files = []
    
    for file in files:
        file_location = f"{upload_dir}/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create statement record
        db_statement = models.Statement(
            card_id=card_id,
            file_path=file_location,
            upload_date=datetime.utcnow()
        )
        db.add(db_statement)
        db.commit()
        db.refresh(db_statement)
        
        # Process statement using card's bank
        try:
            from ..services import extract_transactions, categorizer
            # Use the bank associated with the card
            bank_name = card.bank if card.bank and card.bank != "other" else None
            transactions_data = extract_transactions(file_location, password=password, bank=bank_name)
            
            for t_data in transactions_data:
                # Detect bill payments, cashback, and hidden charges
                description_upper = t_data["description"].upper()
                is_bill_payment = any(h in description_upper for h in ["BBPS", "MB/IB PAYMENT", "NETBANKING TRANSFER", "DUAL PYT"])
                is_cashback = "CASHBACK" in description_upper and t_data.get("is_credit", False)
                is_hidden_charge = any(h in description_upper for h in ["JOINING FEE", "GST", "FUEL SURCHARGE"])
                
                # Use bank-provided category if available, otherwise use ML
                # Override category for hidden charges
                if is_hidden_charge:
                    category = "Hidden Charges"
                elif t_data.get("category"):
                    category = t_data["category"]
                else:
                    category = categorizer.predict(t_data["description"])
                
                db_transaction = models.Transaction(
                    card_id=card_id,
                    statement_id=db_statement.id,
                    date=t_data["date"],
                    description=t_data["description"],
                    amount=t_data["amount"],
                    currency=t_data["currency"],
                    category=category,
                    is_credit=t_data.get("is_credit", False),
                    is_bill_payment=is_bill_payment,
                    is_cashback=is_cashback,
                    is_hidden_charge=is_hidden_charge
                )
                db.add(db_transaction)
            db.commit()
            
            total_processed += len(transactions_data)
            processed_files.append({
                "filename": file.filename,
                "statement_id": db_statement.id,
                "transaction_count": len(transactions_data)
            })
            
        except Exception as e:
            print(f"Error processing statement {file.filename}: {e}")
            processed_files.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "files_processed": len(files),
        "total_transactions": total_processed,
        "details": processed_files
    }

@router.get("/cards/{card_id}/transactions/")
def read_transactions(card_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.card_id == card_id
    ).order_by(models.Transaction.date).all()
    return transactions

@router.get("/cards/{card_id}/report/")
def get_report(card_id: int, db: Session = Depends(get_db)):
    # Get all transactions for the card
    all_transactions = db.query(models.Transaction).filter(
        models.Transaction.card_id == card_id
    ).all()
    
    # Spending calculation logic:
    # 1. Include all debits (is_credit=False) that are NOT bill payments or cashback
    # 2. Include credits (is_credit=True) that are NOT bill payments or cashback as negative (refunds/reversals)
    # 3. Exclude hidden charges from spending
    
    total_spend = 0.0
    spending_transactions = []
    
    for t in all_transactions:
        # Skip hidden charges
        if t.is_hidden_charge:
            continue
        
        # Skip bill payments (these are not spending)
        if t.is_bill_payment:
            continue
        
        # Handle cashback transactions separately
        if t.is_cashback:
            continue
        
        # Debit transactions (normal spending)
        if not t.is_credit:
            total_spend += t.amount
            spending_transactions.append(t)
        else:
            # Credit transactions (refunds/reversals) - reduce spending
            total_spend -= t.amount
            spending_transactions.append(t)
    
    # Calculate total cashback
    # Credits with is_cashback=True add to cashback
    # Debits with is_cashback=True (cashback reversals) subtract from cashback
    total_cashback = 0.0
    cashback_transactions = []
    
    for t in all_transactions:
        if t.is_cashback:
            if t.is_credit:
                # Cashback credit - add to total
                total_cashback += t.amount
                cashback_transactions.append(t)
            else:
                # Cashback reversal (debit) - subtract from total
                total_cashback -= t.amount
                cashback_transactions.append(t)
    
    # Calculate total hidden charges
    hidden_charge_transactions = [t for t in all_transactions if t.is_hidden_charge]
    total_hidden_charges = sum(t.amount for t in hidden_charge_transactions)
    
    # Category breakdown (spending only, excluding hidden charges, bill payments, and cashback)
    # Include both debits and refunds in category breakdown
    category_spend = {}
    for t in spending_transactions:
        if not t.is_credit:
            # Debit - add to category
            category_spend[t.category] = category_spend.get(t.category, 0) + t.amount
        else:
            # Credit (refund) - subtract from category
            category_spend[t.category] = category_spend.get(t.category, 0) - t.amount
    
    # Largest transaction (spending only, debits only for this metric)
    debit_spending = [t for t in spending_transactions if not t.is_credit]
    largest = max(debit_spending, key=lambda t: t.amount) if debit_spending else None
    
    report = {
        "total_spend": total_spend,
        "total_cashback": total_cashback,
        "total_hidden_charges": total_hidden_charges,
        "net_spend": total_spend - total_cashback,
        "category_spend": category_spend,
        "largest_transaction": {
            "description": largest.description,
            "amount": largest.amount,
            "date": largest.date
        } if largest else None,
        "transaction_count": len(debit_spending),
        "cashback_count": len([t for t in cashback_transactions if t.is_credit]),
        "cashback_reversal_count": len([t for t in cashback_transactions if not t.is_credit]),
        "hidden_charge_count": len(hidden_charge_transactions),
        "refund_count": len([t for t in spending_transactions if t.is_credit])
    }
    return report

