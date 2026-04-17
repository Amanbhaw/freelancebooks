"""
AI Reminder Generator — creates personalized, tone-matched invoice follow-ups.
No paid API needed. Uses templates + smart personalization.
"""

from datetime import datetime, timedelta
import random


TONES = {
    'friendly': {
        'greeting': ['Hi {name}', 'Hey {name}', 'Hello {name}'],
        'opener': [
            'Hope you\'re doing great!',
            'Hope all is well on your end!',
            'Trust everything\'s going smoothly!',
            'Hope the week is treating you well!',
        ],
        'body': [
            'Just a quick note — Invoice #{invoice_no} for {amount} was due on {due_date}. No rush at all, just wanted to make sure it didn\'t slip through the cracks.',
            'Friendly reminder that Invoice #{invoice_no} ({amount}) is still outstanding from {due_date}. I know things get busy!',
            'Quick heads up — looks like Invoice #{invoice_no} for {amount} (due {due_date}) is still pending. Totally understand if it got buried.',
        ],
        'cta': [
            'Would love to wrap this up when you get a chance.',
            'Here\'s a quick link to pay: {payment_link}',
            'Let me know if you need anything on my end!',
        ],
        'close': ['Thanks so much!', 'Really appreciate it!', 'Thanks, {sender_name}', 'Cheers!'],
    },
    'professional': {
        'greeting': ['Dear {name}', 'Hello {name}'],
        'opener': [
            'I hope this message finds you well.',
            'Thank you for your continued partnership.',
        ],
        'body': [
            'I\'m writing to follow up on Invoice #{invoice_no} in the amount of {amount}, which was due on {due_date}. As of today, this invoice remains unpaid.',
            'This is a reminder regarding Invoice #{invoice_no} for {amount}, originally due {due_date}. Our records indicate this payment is still outstanding.',
        ],
        'cta': [
            'Please arrange payment at your earliest convenience.',
            'I\'d appreciate it if you could process this payment soon. Payment link: {payment_link}',
            'If payment has already been sent, please disregard this notice.',
        ],
        'close': ['Best regards,\n{sender_name}', 'Sincerely,\n{sender_name}'],
    },
    'firm': {
        'greeting': ['Dear {name}'],
        'opener': [
            'I\'m reaching out regarding an overdue payment that requires your immediate attention.',
        ],
        'body': [
            'Invoice #{invoice_no} for {amount} was due on {due_date} — that\'s {days_overdue} days ago. Despite previous reminders, this invoice remains unpaid.',
            'This is my {reminder_count}rd follow-up regarding Invoice #{invoice_no} ({amount}), now {days_overdue} days past due.',
        ],
        'cta': [
            'Please process this payment within the next 5 business days to avoid any disruption to our working relationship.',
            'I need to receive payment by {final_date}, or I may need to consider additional steps. Payment link: {payment_link}',
        ],
        'close': ['Thank you for your prompt attention.\n{sender_name}'],
    },
    'final_notice': {
        'greeting': ['Dear {name}'],
        'opener': ['This is a final notice regarding an overdue payment.'],
        'body': [
            'Invoice #{invoice_no} for {amount} has been overdue since {due_date} ({days_overdue} days). Multiple reminders have been sent without response.',
            'Despite {reminder_count} previous reminders, Invoice #{invoice_no} ({amount}) remains unpaid after {days_overdue} days.',
        ],
        'cta': [
            'Please arrange payment of {amount} within 7 days. After this period, I will need to explore formal collection options, which neither of us wants.',
            'This is my final attempt to resolve this amicably. Please pay {amount} via {payment_link} within 7 days.',
        ],
        'close': ['Regards,\n{sender_name}'],
    },
}

SUBJECT_LINES = {
    'friendly': [
        'Quick reminder — Invoice #{invoice_no}',
        'Following up on Invoice #{invoice_no} ({amount})',
        'Hey! Invoice #{invoice_no} reminder',
    ],
    'professional': [
        'Payment Reminder: Invoice #{invoice_no} — {amount}',
        'Outstanding Invoice #{invoice_no} — Follow Up',
    ],
    'firm': [
        'OVERDUE: Invoice #{invoice_no} — {days_overdue} days past due',
        'Urgent: Payment Required — Invoice #{invoice_no}',
    ],
    'final_notice': [
        'FINAL NOTICE: Invoice #{invoice_no} — Immediate Payment Required',
        'Last Reminder Before Collections — Invoice #{invoice_no}',
    ],
}


def get_tone_for_day(days_overdue, reminder_count):
    """Auto-select tone based on overdue days."""
    if days_overdue <= 3:
        return 'friendly'
    if days_overdue <= 14:
        return 'professional'
    if days_overdue <= 30:
        return 'firm'
    return 'final_notice'


def generate_reminder(invoice, sender_name='', tone=None):
    """Generate AI-personalized invoice reminder.

    invoice = {
        'invoice_no': '1042',
        'client_name': 'John Smith',
        'client_email': 'john@example.com',
        'amount': 5000.00,
        'currency': 'USD',
        'due_date': '2026-03-15',
        'project_name': 'Website Redesign',
        'payment_link': 'https://paypal.me/...',
        'reminder_count': 1,
    }
    """
    symbols = {'USD': '$', 'GBP': '£', 'EUR': '€', 'INR': '₹'}
    sym = symbols.get(invoice.get('currency', 'USD'), '$')
    amount_str = f"{sym}{invoice.get('amount', 0):,.2f}"

    # Calculate days overdue
    try:
        due = datetime.fromisoformat(str(invoice.get('due_date', '')))
        days_overdue = max(0, (datetime.now() - due).days)
    except Exception:
        days_overdue = 0

    reminder_count = invoice.get('reminder_count', 1)

    # Auto-select tone
    if not tone:
        tone = get_tone_for_day(days_overdue, reminder_count)

    templates = TONES.get(tone, TONES['friendly'])

    # Build variables
    final_date = (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')
    variables = {
        'name': invoice.get('client_name', 'there'),
        'invoice_no': invoice.get('invoice_no', ''),
        'amount': amount_str,
        'due_date': invoice.get('due_date', ''),
        'days_overdue': days_overdue,
        'project_name': invoice.get('project_name', 'the project'),
        'payment_link': invoice.get('payment_link', '[payment link]'),
        'sender_name': sender_name or 'Your Name',
        'reminder_count': reminder_count,
        'final_date': final_date,
    }

    # Generate email
    greeting = random.choice(templates['greeting']).format(**variables)
    opener = random.choice(templates['opener']).format(**variables)
    body = random.choice(templates['body']).format(**variables)
    cta = random.choice(templates['cta']).format(**variables)
    close = random.choice(templates['close']).format(**variables)

    # Add project context if available
    project_line = ''
    if invoice.get('project_name') and tone in ('friendly', 'professional'):
        project_line = f"\n\nRegarding the {invoice['project_name']} project — "

    email_body = f"""{greeting},

{opener}{project_line}

{body}

{cta}

{close}"""

    subject = random.choice(SUBJECT_LINES.get(tone, SUBJECT_LINES['friendly'])).format(**variables)

    return {
        'subject': subject,
        'body': email_body,
        'tone': tone,
        'days_overdue': days_overdue,
        'reminder_number': reminder_count,
        'generated_at': datetime.now().isoformat(),
    }


def generate_sequence(invoice, sender_name=''):
    """Generate full escalation sequence (4 emails)."""
    sequence = []
    days_schedule = [1, 5, 14, 30]
    tones_schedule = ['friendly', 'professional', 'firm', 'final_notice']

    for i, (day, tone) in enumerate(zip(days_schedule, tones_schedule)):
        inv_copy = {**invoice, 'reminder_count': i + 1}
        # Simulate days overdue
        try:
            due = datetime.fromisoformat(str(invoice.get('due_date', '')))
            inv_copy['due_date'] = invoice.get('due_date', '')
        except Exception:
            pass

        reminder = generate_reminder(inv_copy, sender_name, tone=tone)
        reminder['send_on_day'] = day
        reminder['label'] = f"Reminder {i+1} — Day {day} ({tone.replace('_', ' ').title()})"
        sequence.append(reminder)

    return sequence
