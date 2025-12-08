"""
Credit Card Statement Parser with ABC-based architecture.

This module provides an extensible parser framework for extracting transactions
from various credit card statement PDFs. New bank formats can be added by
implementing the BaseParser abstract class.
"""

import pdfplumber
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime

from .utils import (
    parse_amount,
    parse_date,
    clean_description,
    is_footer_row,
    detect_credit_transaction,
    extract_column_indices
)


class BaseParser(ABC):
    """
    Abstract base class for credit card statement parsers.
    
    Each bank should implement a concrete parser class that defines
    how to detect and parse their specific statement format.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the parser name (e.g., 'HDFC', 'Axis')."""
        pass
    
    @abstractmethod
    def can_parse(self, table: List[List]) -> bool:
        """
        Check if this parser can handle the given table structure.
        
        Args:
            table: Extracted table data from PDF
        
        Returns:
            True if this parser can handle the table format, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_transactions(self, table: List[List]) -> List[Dict]:
        """
        Extract transactions from the table.
        
        Args:
            table: Extracted table data from PDF
        
        Returns:
            List of transaction dictionaries with keys:
                - date: datetime object
                - description: str
                - amount: float
                - currency: str
                - is_credit: bool
                - category: Optional[str]
        """
        pass


class HDFCParser(BaseParser):
    """Parser for HDFC Bank credit card statements."""
    
    @property
    def name(self) -> str:
        return "HDFC"
    
    def can_parse(self, table: List[List]) -> bool:
        """
        HDFC statements have a specific single-column format with pipe-delimited data.
        Format: 'DATE| TIME DESCRIPTION AMOUNT'
        """
        if not table or len(table) == 0:
            return False
        
        # HDFC typically has single-column merged rows
        if len(table[0]) != 1:
            return False
        
        # Check if any row matches HDFC pattern
        hdfc_pattern = re.compile(r'\d{2}/\d{2}/\d{4}\s*\|\s*\d{2}:\d{2}')
        for row in table[:5]:  # Check first 5 rows
            if row and isinstance(row[0], str) and hdfc_pattern.search(row[0]):
                return True
        
        return False
    
    def extract_transactions(self, table: List[List]) -> List[Dict]:
        """
        Extract transactions from HDFC bank statement.
        HDFC format: Single column with format: 'DATE| TIME DESCRIPTION AMOUNT'
        """
        transactions = []
        
        # HDFC has single-column merged rows
        if len(table[0]) == 1:
            for row in table:
                if not row:
                    continue
                full_line = row[0]
                if not isinstance(full_line, str):
                    continue
                
                # Regex for HDFC format: Date| Time Description Amount EndChar
                hdfc_pattern = re.compile(
                    r'(?P<date>\d{2}/\d{2}/\d{4})\s*\|\s*(?P<time>\d{2}:\d{2})\s+(?P<desc>.*?)\s+(?P<amount>[\d,]+\.\d{2})\s*[A-Za-z]?$'
                )
                
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
                    if not dt:
                        continue
                    
                    amt = parse_amount(amt_str)
                    desc_str = clean_description(desc_str)
                    
                    transactions.append({
                        "date": dt,
                        "description": desc_str,
                        "amount": amt,
                        "currency": "INR",
                        "is_credit": is_credit,
                        "category": None  # HDFC doesn't provide category
                    })
        
        return transactions


class AxisParser(BaseParser):
    """Parser for Axis Bank credit card statements."""
    
    @property
    def name(self) -> str:
        return "Axis"
    
    def can_parse(self, table: List[List]) -> bool:
        """
        Axis statements have specific headers:
        'DATE', 'TRANSACTION DETAILS', 'MERCHANT CATEGORY', 'AMOUNT (Rs.)'
        """
        if not table or len(table) < 2:
            return False
        
        # Check headers
        raw_headers = table[0]
        if 'PAYMENT SUMMARY' in str(raw_headers[0]).upper():
            raw_headers = table[1] if len(table) > 1 else raw_headers
        
        headers_upper = [str(h).upper().strip() if h else '' for h in raw_headers]
        
        has_date = any('DATE' in h for h in headers_upper)
        has_transaction = any('TRANSACTION' in h for h in headers_upper)
        has_amount = any('AMOUNT' in h for h in headers_upper)
        
        return has_date and has_transaction and has_amount
    
    def extract_transactions(self, table: List[List]) -> List[Dict]:
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
        if 'PAYMENT SUMMARY' in str(raw_headers[0]).upper():
            raw_headers = table[1]
        headers_upper = [str(h).upper().strip() if h else '' for h in raw_headers]
        
        # Find column indices - handle merged cells
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
            if row[0] and is_footer_row(str(row[0])):
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
            
            # Parse amount and detect credit/debit
            amt, is_credit = detect_credit_transaction(str(amt_str).strip())
            if amt == 0:
                continue
            
            # Clean up description
            desc_str = clean_description(desc_str)
            
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


class StandardParser(BaseParser):
    """Fallback parser for generic credit card statement formats."""
    
    @property
    def name(self) -> str:
        return "Standard"
    
    def can_parse(self, table: List[List]) -> bool:
        """
        Check for common table structure with date, description, and amount columns.
        """
        if not table or not table[0]:
            return False
        
        headers = [str(h).lower() for h in table[0] if h]
        
        has_date = any(k in headers for k in ['date', 'transaction date', 'posting date'])
        has_desc = any(k in headers for k in ['description', 'details', 'particulars'])
        has_amount = any(k in headers for k in ['amount', 'debit', 'amt'])
        
        return has_date and has_desc and has_amount
    
    def extract_transactions(self, table: List[List]) -> List[Dict]:
        """
        Extract transactions from standard multi-column table format.
        Fallback parser for generic statements.
        """
        transactions = []
        
        if not table or not table[0]:
            return transactions
        
        headers = [str(h).lower() for h in table[0] if h]
        
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
            
            dt = parse_date(str(d_str).strip())
            if not dt:
                continue
            
            amt = parse_amount(str(amt_str).strip())
            desc_str = clean_description(desc_str)
            
            transactions.append({
                "date": dt,
                "description": desc_str,
                "amount": amt,
                "currency": "INR",
                "is_credit": False,
                "category": None
            })
        
        return transactions


class ParserFactory:
    """
    Factory to manage and select appropriate parsers.
    
    The factory maintains a list of available parsers and selects
    the best one based on table structure or explicit bank hint.
    """
    
    def __init__(self):
        """Initialize factory with all available parsers."""
        self.parsers: List[BaseParser] = [
            HDFCParser(),
            AxisParser(),
            StandardParser()
        ]
    
    def get_parser(self, table: List[List], bank: Optional[str] = None) -> Optional[BaseParser]:
        """
        Get the appropriate parser for the table.
        
        Args:
            table: Extracted table data from PDF
            bank: Optional bank hint ('hdfc', 'axis', etc.)
        
        Returns:
            BaseParser instance that can handle the table, or None if no suitable parser found
        """
        # If bank is specified, try that parser first
        if bank:
            bank_lower = bank.lower()
            for parser in self.parsers:
                if parser.name.lower() == bank_lower:
                    if parser.can_parse(table):
                        return parser
        
        # Auto-detect based on table structure
        for parser in self.parsers:
            if parser.can_parse(table):
                return parser
        
        return None
    
    def add_parser(self, parser: BaseParser):
        """
        Add a custom parser to the factory.
        
        Args:
            parser: Custom parser instance implementing BaseParser
        """
        self.parsers.insert(0, parser)  # Insert at beginning for priority


def extract_transactions(
    file_path: str,
    password: Optional[str] = None,
    bank: Optional[str] = None
) -> List[Dict]:
    """
    Main function to extract transactions from PDF statements.
    
    Uses the parser factory to automatically detect and parse
    different bank statement formats.
    
    Args:
        file_path: Path to the PDF file
        password: Optional password for encrypted PDFs
        bank: Optional bank name to force specific parser ('hdfc', 'axis', etc.)
    
    Returns:
        List of transaction dictionaries
    
    Example:
        >>> transactions = extract_transactions('statement.pdf', password='1234', bank='hdfc')
        >>> print(f"Found {len(transactions)} transactions")
    """
    factory = ParserFactory()
    transactions = []
    
    try:
        with pdfplumber.open(file_path, password=password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        print(f"Processing table with {len(table)} rows, {len(table[0]) if table else 0} columns")
                        
                        parser = factory.get_parser(table, bank)
                        if parser:
                            try:
                                result = parser.extract_transactions(table)
                                if result:
                                    print(f"{parser.name} parser extracted {len(result)} transactions")
                                    transactions.extend(result)
                            except Exception as e:
                                print(f"{parser.name} parser failed: {e}")
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
                                            "description": clean_description(description),
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
