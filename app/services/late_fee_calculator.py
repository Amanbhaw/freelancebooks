"""
Late Fee Calculator — calculates penalties for overdue invoices.
Supports US/UK standard rates.
"""

from datetime import datetime


def calculate_late_fee(amount, due_date, rate_monthly=1.5, max_months=12):
    """Calculate late fee on overdue invoice.

    Standard: 1-1.5% per month (12-18% annually).
    """
    try:
        due = datetime.fromisoformat(str(due_date))
        days_late = max(0, (datetime.now() - due).days)
    except Exception:
        return {'error': 'Invalid due date'}

    if days_late == 0:
        return {
            'days_late': 0,
            'late_fee': 0,
            'total_due': amount,
            'status': 'on_time',
        }

    months_late = min(days_late / 30, max_months)
    late_fee = amount * (rate_monthly / 100) * months_late
    total = amount + late_fee

    if days_late <= 7:
        status = 'slightly_overdue'
        urgency = 'low'
    elif days_late <= 30:
        status = 'overdue'
        urgency = 'medium'
    elif days_late <= 60:
        status = 'seriously_overdue'
        urgency = 'high'
    else:
        status = 'critically_overdue'
        urgency = 'critical'

    return {
        'original_amount': round(amount, 2),
        'days_late': days_late,
        'months_late': round(months_late, 1),
        'rate_monthly': rate_monthly,
        'late_fee': round(late_fee, 2),
        'total_due': round(total, 2),
        'status': status,
        'urgency': urgency,
    }
