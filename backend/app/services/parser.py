import pdfplumber
import re
from typing import List, Dict, Optional
from datetime import datetime

def parse_amount(amount_str: str) -> float:
    # Remove currency symbols (₹, Rs, etc) and commas
    clean_str = re.sub(r'[^\d.-]', '', amount_str)
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

def parse_date(date_str: str) -> Optional[datetime]:
    formats = [
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
        "%d/%m/%y", "%d-%m-%y", "%d.%m.%y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def extract_hdfc_transactions(table: List[List]) -> List[Dict]:
    """
    Extract transactions from HDFC bank statement.
    HDFC format: Single column with format: 'DATE| TIME DESCRIPTION AMOUNT'
    """
    transactions = []
    
    # HDFC has single-column merged rows
    if len(table[0]) == 1:
        for row in table:
            if not row: continue
            full_line = row[0]
            if not isinstance(full_line, str): continue
            
            # Regex for HDFC format: Date| Time Description Amount EndChar
            hdfc_pattern = re.compile(r'(?P<date>\d{2}/\d{2}/\d{4})\s*\|\s*(?P<time>\d{2}:\d{2})\s+(?P<desc>.*?)\s+(?P<amount>[\d,]+\.\d{2})\s*[A-Za-z]?$')
            
            match = hdfc_pattern.search(full_line.replace('\n', ' '))
            if match:
                d_str = match.group('date')
                desc_str = match.group('desc').strip()
                amt_str = match.group('amount')
                
                # Check for credit transaction (+ C suffix)
                is_credit = False
                if desc_str.endswith('+ C'):
                    is_credit = True
                    desc_str = desc_str[:-3].strip()
                elif desc_str.endswith(' C'):
                    desc_str = desc_str[:-2].strip()
                
                dt = parse_date(d_str)
                if not dt: continue
                
                amt = parse_amount(amt_str)
                
                transactions.append({
                    "date": dt,
                    "description": desc_str,
                    "amount": amt,
                    "currency": "INR",
                    "is_credit": is_credit,
                    "category": None  # HDFC doesn't provide category
                })
    
    return transactions


def extract_axis_transactions(table: List[List]) -> List[Dict]:
    """
    Extract transactions from Axis Bank statement.
    Handles two formats:
    1. Standard: ['DATE', 'TRANSACTION DETAILS', 'MERCHANT CATEGORY', 'AMOUNT (Rs.)']
    2. Merged cells: ['DATE', None, 'TRANSACTION DETAILS', None, ..., 'MERCHANT CATEGORY', 'AMOUNT (Rs.)']
    """
    transactions = []
    
    if not table or len(table) < 2:
        return transactions
    
    # Flatten and clean headers, removing None values
    raw_headers = table[0]
    if 'PAYMENT SUMMARY' in raw_headers[0]:
        raw_headers = table[1]
    headers_upper = [str(h).upper().strip() if h else '' for h in raw_headers]
    
    # Check if this looks like an Axis Bank table
    has_date = any('DATE' in h for h in headers_upper)
    has_transaction = any('TRANSACTION' in h for h in headers_upper)
    has_amount = any('AMOUNT' in h for h in headers_upper)
    
    if not (has_date and has_transaction and has_amount):
        return transactions
    
    # Find column indices - handle merged cells by finding first non-empty occurrence
    date_idx = -1
    desc_idx = -1
    category_idx = -1
    amt_idx = -1
    
    for i, h in enumerate(headers_upper):
        if 'DATE' in h and date_idx == -1:
            date_idx = i
        if 'TRANSACTION' in h and desc_idx == -1:
            desc_idx = i
        if 'MERCHANT CATEGORY' in h and category_idx == -1:
            category_idx = i
        if 'AMOUNT' in h and amt_idx == -1:
            amt_idx = i
    
    if date_idx == -1 or desc_idx == -1 or amt_idx == -1:
        return transactions
    
    # Process rows
    for row in table[1:]:
        if not row or len(row) == 0:
            continue
            
        # Skip footer/header rows
        if row[0] and any(skip in str(row[0]).upper() for skip in ['END OF STATEMENT', 'PAYMENT SUMMARY', 'ACCOUNT SUMMARY', 'CARD NO:']):
            continue
        
        # Get values, handling None in merged cells
        d_str = None
        desc_str = None
        amt_str = None
        category_str = None
        
        # For date: check the date column
        if date_idx < len(row):
            d_str = row[date_idx]
        
        # For description: might be in desc_idx or spread across multiple cells
        # Collect all non-None, non-empty values between desc_idx and category_idx
        if desc_idx < len(row):
            desc_parts = []
            end_idx = category_idx if category_idx != -1 else amt_idx
            for i in range(desc_idx, min(end_idx, len(row))):
                if row[i] and str(row[i]).strip() and str(row[i]).strip().upper() not in ['', 'NONE']:
                    desc_parts.append(str(row[i]).strip())
            desc_str = ' '.join(desc_parts) if desc_parts else None
        
        # For category
        if category_idx != -1 and category_idx < len(row):
            category_str = row[category_idx]
        
        # For amount
        if amt_idx < len(row):
            amt_str = row[amt_idx]
        
        # Validate we have minimum required fields
        if not d_str or not desc_str or not amt_str:
            continue
        
        # Parse date
        dt = parse_date(str(d_str).strip())
        if not dt:
            continue
        
        # Check if it's credit or debit
        is_credit = False
        amt_str = str(amt_str).strip()
        if amt_str.endswith(' Cr'):
            is_credit = True
            amt_str = amt_str[:-3].strip()
        elif amt_str.endswith(' Dr'):
            amt_str = amt_str[:-3].strip()
        
        amt = parse_amount(amt_str)
        if amt == 0:
            continue
        
        # Clean up description
        desc_str = str(desc_str).replace('\n', ' ').strip()
        
        # Use bank-provided category or None
        category = category_str.strip() if category_str and str(category_str).strip() else None
        
        transactions.append({
            "date": dt,
            "description": desc_str,
            "amount": amt,
            "currency": "INR",
            "is_credit": is_credit,
            "category": category
        })
    
    return transactions


def extract_standard_table_transactions(table: List[List]) -> List[Dict]:
    """
    Extract transactions from standard multi-column table format.
    Fallback parser for generic statements.
    """
    transactions = []
    
    if not table or not table[0]:
        return transactions
    
    headers = [str(h).lower() for h in table[0] if h]
    
    # Check for common headers
    if not (any(k in headers for k in ['date', 'transaction date', 'posting date']) and
            any(k in headers for k in ['description', 'details', 'particulars']) and
            any(k in headers for k in ['amount', 'debit', 'amt'])):
        return transactions
    
    # Identify indices
    date_idx = -1
    desc_idx = -1
    amt_idx = -1
    
    for i, h in enumerate(headers):
        if 'date' in h and date_idx == -1:
            date_idx = i
        if ('description' in h or 'details' in h or 'particulars' in h) and desc_idx == -1:
            desc_idx = i
        if ('amount' in h or 'debit' in h) and amt_idx == -1:
            amt_idx = i
    
    if date_idx == -1 or desc_idx == -1 or amt_idx == -1:
        return transactions
    
    # Parse rows
    for row in table[1:]:
        if len(row) <= max(date_idx, desc_idx, amt_idx):
            continue
        
        d_str = row[date_idx]
        desc_str = row[desc_idx]
        amt_str = row[amt_idx]
        
        if not d_str or not desc_str or not amt_str:
            continue
        
        desc_str = desc_str.replace('\n', ' ')
        dt = parse_date(d_str)
        if not dt:
            continue
        
        amt = parse_amount(amt_str)
        
        transactions.append({
            "date": dt,
            "description": desc_str,
            "amount": amt,
            "currency": "INR",
            "is_credit": False,
            "category": None
        })
    
    return transactions


def extract_transactions(file_path: str, password: Optional[str] = None, bank: Optional[str] = None) -> List[Dict]:
    """
    Main function to extract transactions from PDF statements.
    Tries different bank-specific parsers based on table structure.
    
    Args:
        file_path: Path to the PDF file
        password: Optional password for encrypted PDFs
        bank: Optional bank name to force specific parser ('hdfc', 'axis', etc.)
    
    Returns:
        List of transaction dictionaries
    """
    transactions = []
    
    try:
        with pdfplumber.open(file_path, password=password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        print(f"Processing table with {len(table)} rows, {len(table[0]) if table else 0} columns")
                        
                        # Try bank-specific parsers in order
                        parsers = []
                        
                        if bank == 'hdfc' or bank is None:
                            parsers.append(('HDFC', extract_hdfc_transactions))
                        if bank == 'axis' or bank is None:
                            parsers.append(('Axis', extract_axis_transactions))
                        if bank is None:
                            parsers.append(('Standard', extract_standard_table_transactions))
                        
                        for parser_name, parser_func in parsers:
                            try:
                                result = parser_func(table)
                                if result:
                                    print(f"{parser_name} parser extracted {len(result)} transactions")
                                    transactions.extend(result)
                                    break  # Stop trying other parsers if we got results
                            except Exception as e:
                                print(f"{parser_name} parser failed: {e}")
                                continue
                
                # Fallback to text extraction if no tables found
                if not transactions:
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    lines = text.split('\n')
                    date_pattern = re.compile(r'(\d{2}/\d{2}/\d{4})')
                    
                    for line in lines:
                        match = date_pattern.search(line)
                        if match:
                            parts = line.split()
                            if len(parts) > 3:
                                date_str = match.group(0)
                                amount_part = parts[-1]
                                
                                if not re.match(r'[\d,.-]+(Cr|Dr)?$', amount_part):
                                    continue
                                
                                amt = parse_amount(amount_part)
                                if amt == 0:
                                    continue
                                
                                desc_start = line.find(date_str) + len(date_str)
                                desc_end = line.rfind(amount_part)
                                if desc_end > desc_start:
                                    description = line[desc_start:desc_end].strip()
                                    dt = parse_date(date_str)
                                    if dt:
                                        transactions.append({
                                            "date": dt,
                                            "description": description,
                                            "amount": amt,
                                            "currency": "INR",
                                            "is_credit": False,
                                            "category": None
                                        })
    
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        pass
    
    print(f"Total transactions extracted: {len(transactions)}")
    return transactions
