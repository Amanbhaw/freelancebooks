"""
CSV Parser — handles bank statement CSVs from major banks.
Auto-detects format (US/UK/Indian banks).
Sanitizes input for security.
"""

import csv
import io
import re
from datetime import datetime


# Common bank CSV column name patterns
DATE_COLUMNS = ['date', 'transaction date', 'posting date', 'value date',
                'txn date', 'trans date', 'booked date']
DESC_COLUMNS = ['description', 'memo', 'narrative', 'details', 'particulars',
                'transaction description', 'reference', 'payee', 'name']
AMOUNT_COLUMNS = ['amount', 'value', 'sum', 'transaction amount']
DEBIT_COLUMNS = ['debit', 'withdrawal', 'money out', 'dr']
CREDIT_COLUMNS = ['credit', 'deposit', 'money in', 'cr']

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB max
MAX_ROWS = 50000


def sanitize_text(text):
    """Remove potentially dangerous characters from CSV fields."""
    if not text:
        return ''
    text = str(text).strip()
    # Prevent CSV injection (formula injection)
    if text and text[0] in ('=', '+', '-', '@', '\t', '\r', '\n'):
        text = "'" + text
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text[:500]  # Max 500 chars per field


def parse_amount(value):
    """Parse amount string → float. Handles various formats."""
    if not value:
        return 0.0
    value = str(value).strip()
    # Remove currency symbols and spaces
    value = re.sub(r'[£$€₹,\s]', '', value)
    # Handle parentheses as negative (accounting format)
    if value.startswith('(') and value.endswith(')'):
        value = '-' + value[1:-1]
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def find_column(headers, patterns):
    """Find matching column index from header patterns."""
    for i, h in enumerate(headers):
        h_lower = h.lower().strip()
        for pat in patterns:
            if pat in h_lower:
                return i
    return -1


def parse_csv(file_content, filename=''):
    """Parse bank CSV → list of {date, description, amount}.

    Security:
    - File size limit (10 MB)
    - Row limit (50K)
    - Input sanitization
    - No formula injection
    """
    # Size check
    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(f"File too large. Max {MAX_FILE_SIZE // 1024 // 1024} MB.")

    # Decode if bytes
    if isinstance(file_content, bytes):
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                file_content = file_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

    # Parse CSV
    reader = csv.reader(io.StringIO(file_content))
    rows = list(reader)

    if len(rows) < 2:
        raise ValueError("CSV must have header row + at least 1 data row.")

    if len(rows) > MAX_ROWS:
        raise ValueError(f"Too many rows. Max {MAX_ROWS}.")

    # Find columns
    headers = [sanitize_text(h) for h in rows[0]]
    date_col = find_column(headers, DATE_COLUMNS)
    desc_col = find_column(headers, DESC_COLUMNS)
    amount_col = find_column(headers, AMOUNT_COLUMNS)
    debit_col = find_column(headers, DEBIT_COLUMNS)
    credit_col = find_column(headers, CREDIT_COLUMNS)

    if date_col == -1:
        raise ValueError("Could not find date column. Expected: Date, Transaction Date, etc.")

    if desc_col == -1:
        # Try second column as description (common fallback)
        desc_col = 1 if len(headers) > 1 else -1

    # Parse transactions
    transactions = []
    for row_num, row in enumerate(rows[1:], start=2):
        if not row or all(not cell.strip() for cell in row):
            continue  # Skip empty rows

        try:
            # Date
            date_str = sanitize_text(row[date_col]) if date_col < len(row) else ''
            if not date_str:
                continue

            # Description
            desc = sanitize_text(row[desc_col]) if desc_col >= 0 and desc_col < len(row) else ''

            # Amount
            if amount_col >= 0 and amount_col < len(row):
                amount = parse_amount(row[amount_col])
            elif debit_col >= 0 and credit_col >= 0:
                debit = parse_amount(row[debit_col]) if debit_col < len(row) else 0
                credit = parse_amount(row[credit_col]) if credit_col < len(row) else 0
                amount = credit - debit  # Positive = income, negative = expense
            else:
                # Try third column
                amount = parse_amount(row[2]) if len(row) > 2 else 0

            if amount == 0 and not desc:
                continue  # Skip meaningless rows

            transactions.append({
                'date': date_str,
                'description': desc,
                'amount': round(amount, 2),
                'row_number': row_num,
            })

        except (IndexError, ValueError):
            continue  # Skip malformed rows

    if not transactions:
        raise ValueError("No valid transactions found. Check CSV format.")

    return transactions
