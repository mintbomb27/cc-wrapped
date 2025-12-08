from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # e.g., "Chase Sapphire"
    last_4_digits = Column(String(4))
    bank = Column(String, default="other")  # 'hdfc', 'axis', 'other'
    
    statements = relationship("Statement", back_populates="card")
    transactions = relationship("Transaction", back_populates="card")

class Statement(Base):
    __tablename__ = "statements"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"))
    file_path = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    card = relationship("Card", back_populates="statements")
    transactions = relationship("Transaction", back_populates="statement")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"))
    statement_id = Column(Integer, ForeignKey("statements.id"))
    date = Column(DateTime)
    description = Column(String)
    amount = Column(Float)
    currency = Column(String, default="INR")
    category = Column(String, default="Uncategorized")
    is_credit = Column(Boolean, default=False)
    is_bill_payment = Column(Boolean, default=False)
    is_cashback = Column(Boolean, default=False)
    is_hidden_charge = Column(Boolean, default=False)
    
    card = relationship("Card", back_populates="transactions")
    statement = relationship("Statement", back_populates="transactions")
