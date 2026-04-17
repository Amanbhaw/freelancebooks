"""
Invoice Generator — create professional invoices (Tabby has basic, ours is better).
Generates HTML invoices that can be printed/PDF'd.
"""

from datetime import datetime, timedelta
import random
import string


def generate_invoice_number():
    """Generate unique invoice number."""
    date_part = datetime.now().strftime('%Y%m%d')
    rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"INV-{date_part}-{rand_part}"


def create_invoice(data):
    """Create professional invoice HTML.

    data = {
        'from_name': 'Your Name',
        'from_email': 'you@email.com',
        'from_address': 'Your Address',
        'to_name': 'Client Name',
        'to_email': 'client@email.com',
        'to_address': 'Client Address',
        'items': [
            {'description': 'Web Development', 'quantity': 40, 'rate': 50},
        ],
        'currency': 'USD',
        'tax_rate': 0,
        'notes': 'Payment due within 30 days',
        'due_days': 30,
    }
    """
    invoice_no = generate_invoice_number()
    today = datetime.now()
    due_date = today + timedelta(days=data.get('due_days', 30))

    items = data.get('items', [])
    currency = data.get('currency', 'USD')
    symbols = {'USD': '$', 'GBP': '£', 'EUR': '€', 'INR': '₹'}
    sym = symbols.get(currency, '$')

    subtotal = sum(item['quantity'] * item['rate'] for item in items)
    tax_rate = data.get('tax_rate', 0)
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount

    # Build items rows
    items_html = ''
    for item in items:
        amount = item['quantity'] * item['rate']
        items_html += f'''
        <tr>
            <td style="padding:12px;border-bottom:1px solid #e2e8f0">{item['description']}</td>
            <td style="padding:12px;border-bottom:1px solid #e2e8f0;text-align:center">{item['quantity']}</td>
            <td style="padding:12px;border-bottom:1px solid #e2e8f0;text-align:right">{sym}{item['rate']:,.2f}</td>
            <td style="padding:12px;border-bottom:1px solid #e2e8f0;text-align:right">{sym}{amount:,.2f}</td>
        </tr>'''

    html = f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Invoice {invoice_no}</title></head>
<body style="font-family:-apple-system,sans-serif;max-width:800px;margin:0 auto;padding:40px;color:#1e293b">

<div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:40px">
    <div>
        <h1 style="color:#0f172a;margin:0;font-size:2rem">INVOICE</h1>
        <p style="color:#64748b;margin:5px 0">#{invoice_no}</p>
    </div>
    <div style="text-align:right">
        <p style="margin:2px 0"><strong>Date:</strong> {today.strftime('%B %d, %Y')}</p>
        <p style="margin:2px 0"><strong>Due:</strong> {due_date.strftime('%B %d, %Y')}</p>
        <p style="margin:2px 0;padding:4px 12px;background:#fee2e2;color:#dc2626;border-radius:4px;display:inline-block;font-size:0.85rem">
            Due in {data.get('due_days', 30)} days
        </p>
    </div>
</div>

<div style="display:flex;justify-content:space-between;margin-bottom:30px">
    <div style="flex:1">
        <p style="color:#64748b;margin:0 0 5px;font-size:0.85rem;text-transform:uppercase">From</p>
        <p style="margin:2px 0;font-weight:600">{data.get('from_name', '')}</p>
        <p style="margin:2px 0;color:#64748b">{data.get('from_email', '')}</p>
        <p style="margin:2px 0;color:#64748b">{data.get('from_address', '')}</p>
    </div>
    <div style="flex:1;text-align:right">
        <p style="color:#64748b;margin:0 0 5px;font-size:0.85rem;text-transform:uppercase">Bill To</p>
        <p style="margin:2px 0;font-weight:600">{data.get('to_name', '')}</p>
        <p style="margin:2px 0;color:#64748b">{data.get('to_email', '')}</p>
        <p style="margin:2px 0;color:#64748b">{data.get('to_address', '')}</p>
    </div>
</div>

<table style="width:100%;border-collapse:collapse;margin:20px 0">
    <thead>
        <tr style="background:#f1f5f9">
            <th style="padding:12px;text-align:left;border-bottom:2px solid #cbd5e1">Description</th>
            <th style="padding:12px;text-align:center;border-bottom:2px solid #cbd5e1">Qty/Hours</th>
            <th style="padding:12px;text-align:right;border-bottom:2px solid #cbd5e1">Rate</th>
            <th style="padding:12px;text-align:right;border-bottom:2px solid #cbd5e1">Amount</th>
        </tr>
    </thead>
    <tbody>{items_html}</tbody>
</table>

<div style="display:flex;justify-content:flex-end;margin:20px 0">
    <div style="width:250px">
        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #e2e8f0">
            <span>Subtotal</span><span>{sym}{subtotal:,.2f}</span>
        </div>
        {"<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #e2e8f0'><span>Tax (" + str(tax_rate) + "%)</span><span>" + sym + f"{tax_amount:,.2f}</span></div>" if tax_rate > 0 else ""}
        <div style="display:flex;justify-content:space-between;padding:12px 0;font-size:1.2rem;font-weight:700;border-top:2px solid #0f172a">
            <span>Total</span><span>{sym}{total:,.2f}</span>
        </div>
    </div>
</div>

{"<div style='margin:20px 0;padding:15px;background:#f8fafc;border-radius:8px;border-left:4px solid #38bdf8'><strong>Notes:</strong> " + data.get('notes', '') + "</div>" if data.get('notes') else ""}

<div style="margin-top:40px;padding-top:20px;border-top:1px solid #e2e8f0;text-align:center;color:#94a3b8;font-size:0.8rem">
    <p>Generated by BooksBird AI | booksbird.com</p>
</div>
</body></html>'''

    return {
        'invoice_number': invoice_no,
        'html': html,
        'subtotal': subtotal,
        'tax': tax_amount,
        'total': total,
        'currency': currency,
        'due_date': due_date.isoformat(),
    }
