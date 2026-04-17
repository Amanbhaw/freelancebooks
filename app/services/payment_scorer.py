"""
Payment Scorer — predicts client payment behavior.
Assigns A-F score based on history.
"""

from datetime import datetime


def score_client(payment_history):
    """Score a client's payment reliability.

    payment_history = [
        {'invoice_no': '1001', 'amount': 5000, 'due_date': '2026-01-15', 'paid_date': '2026-01-14', 'status': 'paid'},
        {'invoice_no': '1002', 'amount': 3000, 'due_date': '2026-02-15', 'paid_date': '2026-02-25', 'status': 'paid'},
        {'invoice_no': '1003', 'amount': 4500, 'due_date': '2026-03-15', 'paid_date': None, 'status': 'unpaid'},
    ]
    """
    if not payment_history:
        return {
            'score': 'N',
            'label': 'New Client — No History',
            'recommendation': 'Consider requesting 50% upfront deposit for first project.',
            'risk_level': 'unknown',
            'avg_days_late': 0,
            'on_time_rate': 0,
        }

    total = len(payment_history)
    paid = [p for p in payment_history if p.get('status') == 'paid']
    unpaid = [p for p in payment_history if p.get('status') in ('unpaid', 'overdue')]

    # Calculate on-time rate
    on_time = 0
    late_days = []
    total_owed = sum(p.get('amount', 0) for p in unpaid)

    for p in paid:
        try:
            due = datetime.fromisoformat(str(p['due_date']))
            paid_on = datetime.fromisoformat(str(p['paid_date']))
            diff = (paid_on - due).days
            if diff <= 0:
                on_time += 1
            else:
                late_days.append(diff)
        except Exception:
            pass

    on_time_rate = (on_time / max(len(paid), 1)) * 100
    avg_late = sum(late_days) / max(len(late_days), 1) if late_days else 0
    unpaid_rate = (len(unpaid) / max(total, 1)) * 100

    # Calculate score
    if on_time_rate >= 90 and unpaid_rate == 0:
        score, label = 'A', 'Excellent Payer'
        risk = 'very_low'
        rec = 'Reliable client. Standard payment terms are fine.'
    elif on_time_rate >= 70 and unpaid_rate <= 10:
        score, label = 'B', 'Good Payer'
        risk = 'low'
        rec = 'Generally reliable. Send gentle reminders on due date.'
    elif on_time_rate >= 50 or avg_late <= 14:
        score, label = 'C', 'Average Payer'
        risk = 'medium'
        rec = 'Often late. Start reminders 3 days before due date. Consider milestone payments.'
    elif on_time_rate >= 30 or avg_late <= 30:
        score, label = 'D', 'Slow Payer'
        risk = 'high'
        rec = 'Frequently late. Require 50% upfront deposit. Start reminders immediately upon sending invoice.'
    else:
        score, label = 'F', 'High Risk'
        risk = 'very_high'
        rec = 'Very unreliable. Require full upfront payment or milestone-based billing. Consider dropping this client.'

    return {
        'score': score,
        'label': label,
        'risk_level': risk,
        'recommendation': rec,
        'total_invoices': total,
        'paid_count': len(paid),
        'unpaid_count': len(unpaid),
        'on_time_rate': round(on_time_rate, 1),
        'avg_days_late': round(avg_late, 1),
        'total_outstanding': round(total_owed, 2),
    }


def predict_payment_date(client_score, due_date):
    """Predict when client will actually pay based on score."""
    try:
        due = datetime.fromisoformat(str(due_date))
    except Exception:
        return None

    delays = {
        'A': 0,    # On time
        'B': 3,    # 3 days late
        'C': 10,   # 10 days late
        'D': 21,   # 3 weeks late
        'F': 45,   # 6+ weeks late
        'N': 7,    # Unknown, assume 1 week
    }
    delay = delays.get(client_score, 7)
    predicted = due + __import__('datetime').timedelta(days=delay)

    return {
        'due_date': due_date,
        'predicted_payment': predicted.date().isoformat(),
        'expected_delay_days': delay,
        'confidence': {
            'A': '95%', 'B': '85%', 'C': '70%',
            'D': '50%', 'F': '30%', 'N': '60%',
        }.get(client_score, '50%'),
    }


def generate_cashflow_forecast(invoices_with_scores):
    """Predict cash flow for next 30/60/90 days."""
    forecast = {'30_days': 0, '60_days': 0, '90_days': 0, 'at_risk': 0, 'details': []}
    now = datetime.now()

    for inv in invoices_with_scores:
        amount = inv.get('amount', 0)
        score = inv.get('client_score', 'N')
        prediction = predict_payment_date(score, inv.get('due_date', now.isoformat()))

        if prediction:
            try:
                pred_date = datetime.fromisoformat(prediction['predicted_payment'])
                days_out = (pred_date - now).days

                if days_out <= 30:
                    forecast['30_days'] += amount
                elif days_out <= 60:
                    forecast['60_days'] += amount
                elif days_out <= 90:
                    forecast['90_days'] += amount

                if score in ('D', 'F'):
                    forecast['at_risk'] += amount

                forecast['details'].append({
                    'invoice': inv.get('invoice_no'),
                    'amount': amount,
                    'client': inv.get('client_name'),
                    'score': score,
                    'predicted_payment': prediction['predicted_payment'],
                    'confidence': prediction['confidence'],
                })
            except Exception:
                pass

    forecast['total_expected'] = forecast['30_days'] + forecast['60_days'] + forecast['90_days']
    return forecast
