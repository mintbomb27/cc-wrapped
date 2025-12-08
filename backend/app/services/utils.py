"""
Utility functions for parsing credit card statements.

This module contains common helper functions used across different
bank statement parsers for cleaning and parsing transaction data.
"""

import re
from typing import Optional, Tuple
from datetime import datetime


def parse_amount(amount_str: str) -> float:
    """
    Parse and clean amount strings to float values.
    
    Removes currency symbols (₹, Rs, etc), commas, and other non-numeric characters.
    
    Args:
        amount_str: String containing the amount (e.g., "₹1,234.56", "Rs. 500")
    
    Returns:
        Parsed amount as float, or 0.0 if parsing fails
    
    Examples:
        >>> parse_amount("₹1,234.56")
        1234.56
        >>> parse_amount("Rs. 500")
        500.0
    """
    # Remove currency symbols (₹, Rs, etc) and commas
    clean_str = re.sub(r'[^\d.-]', '', amount_str)
    try:
        return float(clean_str)
    except ValueError:
        return 0.0


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date strings with multiple format support.
    
    Tries common Indian date formats (DD/MM/YYYY, DD-MM-YYYY, etc.)
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        Parsed datetime object, or None if parsing fails
    
    Examples:
        >>> parse_date("31/12/2023")
        datetime(2023, 12, 31, 0, 0)
        >>> parse_date("01-01-24")
        datetime(2024, 1, 1, 0, 0)
    """
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


def clean_description(desc: str) -> str:
    """
    Clean and normalize transaction descriptions.
    
    Removes excessive whitespace, newlines, and normalizes spacing.
    
    Args:
        desc: Raw description string
    
    Returns:
        Cleaned description string
    
    Examples:
        >>> clean_description("AMAZON\\n  PAYMENT  ")
        'AMAZON PAYMENT'
    """
    if not desc:
        return ""
    
    # Replace newlines with spaces
    cleaned = desc.replace('\n', ' ')
    # Normalize multiple spaces to single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    # Strip leading/trailing whitespace
    return cleaned.strip()


def is_footer_row(row_text: str) -> bool:
    """
    Detect if a row is a footer or header row that should be skipped.
    
    Args:
        row_text: Text content of the row (typically first cell)
    
    Returns:
        True if this is a footer/header row, False otherwise
    
    Examples:
        >>> is_footer_row("END OF STATEMENT")
        True
        >>> is_footer_row("PAYMENT SUMMARY")
        True
        >>> is_footer_row("Regular transaction")
        False
    """
    if not row_text:
        return False
    
    text_upper = str(row_text).upper()
    skip_patterns = [
        'END OF STATEMENT',
        'PAYMENT SUMMARY',
        'ACCOUNT SUMMARY',
        'CARD NO:',
        'TOTAL AMOUNT',
        'OPENING BALANCE',
        'CLOSING BALANCE',
        'STATEMENT PERIOD'
    ]
    
    return any(pattern in text_upper for pattern in skip_patterns)


def detect_credit_transaction(amount_str: str, desc: str = "") -> Tuple[float, bool]:
    """
    Parse amount and detect if transaction is a credit (refund/cashback) or debit.
    
    Many banks suffix amounts with 'Cr' for credit and 'Dr' for debit.
    
    Args:
        amount_str: Amount string that may contain Cr/Dr suffix
        desc: Optional description to help detect credits
    
    Returns:
        Tuple of (parsed_amount, is_credit)
    
    Examples:
        >>> detect_credit_transaction("1,000.00 Cr")
        (1000.0, True)
        >>> detect_credit_transaction("500.00 Dr")
        (500.0, False)
        >>> detect_credit_transaction("250.00")
        (250.0, False)
    """
    is_credit = False
    amount_str = str(amount_str).strip()
    
    # Check for Cr/Dr suffix
    if amount_str.endswith(' Cr'):
        is_credit = True
        amount_str = amount_str[:-3].strip()
    elif amount_str.endswith(' Dr'):
        amount_str = amount_str[:-3].strip()
    
    # Some formats use + for credit
    if amount_str.startswith('+'):
        is_credit = True
        amount_str = amount_str[1:].strip()
    
    amount = parse_amount(amount_str)
    return amount, is_credit


def extract_column_indices(headers: list, required_columns: dict) -> dict:
    """
    Extract column indices from table headers.
    
    Args:
        headers: List of header strings
        required_columns: Dict mapping logical names to possible header variations
            Example: {'date': ['DATE', 'TRANSACTION DATE', 'POSTING DATE']}
    
    Returns:
        Dict mapping logical names to column indices (or -1 if not found)
    
    Examples:
        >>> headers = ['DATE', 'DESCRIPTION', 'AMOUNT']
        >>> required = {'date': ['DATE'], 'desc': ['DESCRIPTION', 'DETAILS']}
        >>> extract_column_indices(headers, required)
        {'date': 0, 'desc': 1}
    """
    headers_upper = [str(h).upper().strip() if h else '' for h in headers]
    indices = {}
    
    for logical_name, possible_values in required_columns.items():
        indices[logical_name] = -1
        for i, header in enumerate(headers_upper):
            if any(val in header for val in possible_values):
                indices[logical_name] = i
                break
    
    return indices
