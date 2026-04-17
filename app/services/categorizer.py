"""
AI Expense Categorizer — auto-classifies bank transactions.
Uses keyword matching + fuzzy logic (no paid API needed).
Handles US + UK freelancer deduction rules.
"""

import re
from datetime import datetime


# IRS-aligned categories for US freelancers (Schedule C)
CATEGORIES = {
    'advertising': {
        'keywords': ['facebook ads', 'google ads', 'meta ads', 'ad spend', 'marketing',
                     'promotion', 'billboard', 'flyer', 'banner', 'campaign', 'adwords',
                     'linkedin ads', 'twitter ads', 'instagram ads', 'tiktok ads'],
        'deductible': True,
        'irs_line': 'Line 8 - Advertising',
        'hmrc_category': 'Advertising and marketing',
    },
    'car_transport': {
        'keywords': ['uber', 'lyft', 'ola', 'taxi', 'cab', 'fuel', 'petrol', 'diesel',
                     'gas station', 'parking', 'toll', 'metro', 'train ticket', 'bus',
                     'flight', 'airline', 'airways', 'mileage', 'car wash', 'car repair'],
        'deductible': True,
        'irs_line': 'Line 9 - Car & truck expenses',
        'hmrc_category': 'Travel costs',
    },
    'insurance': {
        'keywords': ['insurance', 'health insurance', 'liability', 'indemnity', 'coverage',
                     'premium', 'policy renewal'],
        'deductible': True,
        'irs_line': 'Line 15 - Insurance',
        'hmrc_category': 'Insurance',
    },
    'office_supplies': {
        'keywords': ['staples', 'office depot', 'paper', 'printer', 'ink', 'toner',
                     'pen', 'notebook', 'stationery', 'desk', 'chair', 'monitor',
                     'keyboard', 'mouse', 'usb', 'cable', 'headphones', 'webcam',
                     'amazon', 'flipkart'],
        'deductible': True,
        'irs_line': 'Line 22 - Supplies',
        'hmrc_category': 'Office supplies',
    },
    'software_subscriptions': {
        'keywords': ['github', 'gitlab', 'aws', 'azure', 'google cloud', 'gcp',
                     'digitalocean', 'heroku', 'vercel', 'netlify', 'render', 'railway',
                     'figma', 'canva', 'adobe', 'photoshop', 'slack', 'notion', 'zoom',
                     'microsoft 365', 'dropbox', 'google workspace', 'chatgpt', 'openai',
                     'anthropic', 'cursor', 'copilot', 'saas', 'subscription', 'apple',
                     'spotify', 'netflix', 'domain', 'hosting', 'cloudflare', 'namecheap',
                     'godaddy', 'stripe fee', 'paypal fee', 'razorpay', 'twilio', 'sendgrid',
                     'mailchimp', 'hubspot', 'intercom', 'freshdesk', 'jira', 'trello',
                     'linear', 'monday.com', 'asana', 'clickup', 'grammarly', 'loom'],
        'deductible': True,
        'irs_line': 'Line 27a - Other expenses (software)',
        'hmrc_category': 'Software and IT costs',
    },
    'professional_services': {
        'keywords': ['lawyer', 'attorney', 'legal', 'accountant', 'cpa', 'bookkeeper',
                     'consultant', 'freelancer payment', 'contractor', 'fiverr', 'upwork',
                     'consulting fee', 'advisory'],
        'deductible': True,
        'irs_line': 'Line 17 - Legal & professional services',
        'hmrc_category': 'Accountancy and legal fees',
    },
    'meals_entertainment': {
        'keywords': ['restaurant', 'cafe', 'coffee', 'starbucks', 'lunch', 'dinner',
                     'breakfast', 'food', 'doordash', 'grubhub', 'ubereats', 'swiggy',
                     'zomato', 'mcdonalds', 'subway', 'pizza', 'client dinner',
                     'client lunch', 'meeting meal', 'business meal'],
        'deductible': True,
        'deduction_rate': 0.50,  # 50% deductible in US
        'irs_line': 'Line 24b - Meals (50%)',
        'hmrc_category': 'Business entertainment (limited)',
    },
    'education_training': {
        'keywords': ['udemy', 'coursera', 'pluralsight', 'skillshare', 'masterclass',
                     'conference', 'workshop', 'seminar', 'webinar', 'training', 'course',
                     'certification', 'exam fee', 'book', 'ebook', 'kindle', 'oreilly',
                     'learning', 'tuition'],
        'deductible': True,
        'irs_line': 'Line 27a - Education & training',
        'hmrc_category': 'Training courses',
    },
    'rent_office': {
        'keywords': ['rent', 'lease', 'coworking', 'wework', 'regus', 'office space',
                     'home office', 'workspace'],
        'deductible': True,
        'irs_line': 'Line 20b - Rent (other business property)',
        'hmrc_category': 'Premises costs',
    },
    'phone_internet': {
        'keywords': ['phone bill', 'mobile', 'internet', 'wifi', 'broadband', 'isp',
                     'verizon', 'at&t', 'vodafone', 'jio', 'airtel', 'bt', 'data plan',
                     'hotspot'],
        'deductible': True,
        'deduction_rate': 0.50,  # Often 50% if mixed personal/business
        'irs_line': 'Line 25 - Utilities',
        'hmrc_category': 'Telephone and internet',
    },
    'bank_fees': {
        'keywords': ['bank fee', 'wire transfer', 'atm fee', 'overdraft', 'service charge',
                     'monthly fee', 'account fee', 'transaction fee', 'forex fee',
                     'currency conversion', 'wise fee', 'revolut'],
        'deductible': True,
        'irs_line': 'Line 27a - Bank charges',
        'hmrc_category': 'Bank charges',
    },
    'equipment': {
        'keywords': ['laptop', 'computer', 'macbook', 'ipad', 'tablet', 'phone purchase',
                     'iphone', 'samsung', 'camera', 'microphone', 'tripod', 'ring light',
                     'server', 'hardware', 'ssd', 'ram', 'gpu'],
        'deductible': True,
        'irs_line': 'Line 13 - Depreciation / Section 179',
        'hmrc_category': 'Capital allowances',
    },
    'income': {
        'keywords': ['salary', 'payment received', 'invoice paid', 'client payment',
                     'freelance income', 'project payment', 'deposit', 'transfer in',
                     'credit', 'refund received'],
        'deductible': False,
        'irs_line': 'Line 1 - Gross receipts',
        'hmrc_category': 'Turnover/Income',
    },
    'personal': {
        'keywords': ['grocery', 'supermarket', 'walmart', 'target', 'clothing', 'gym',
                     'netflix', 'spotify', 'entertainment', 'movie', 'shopping',
                     'personal', 'gift', 'donation', 'charity', 'medical', 'pharmacy',
                     'doctor', 'hospital'],
        'deductible': False,
        'irs_line': 'N/A - Personal expense',
        'hmrc_category': 'Not allowable',
    },
    'transfer': {
        'keywords': ['transfer to', 'transfer from', 'moved to savings', 'internal transfer',
                     'credit card payment', 'loan payment', 'emi', 'mortgage'],
        'deductible': False,
        'irs_line': 'N/A - Transfer',
        'hmrc_category': 'Not applicable',
    },
}


def categorize_transaction(description, amount=0):
    """Categorize a single transaction based on description text."""
    desc_lower = description.lower().strip()
    best_category = 'uncategorized'
    best_score = 0

    for category, info in CATEGORIES.items():
        score = 0
        for keyword in info['keywords']:
            if keyword in desc_lower:
                # Longer keyword matches score higher (more specific)
                score = max(score, len(keyword))

        if score > best_score:
            best_score = score
            best_category = category

    # Income detection by amount (positive = income for many banks)
    if best_category == 'uncategorized' and amount > 0:
        # Large positive amounts likely income
        if amount >= 500:
            best_category = 'income'

    cat_info = CATEGORIES.get(best_category, {})
    deduction_rate = cat_info.get('deduction_rate', 1.0) if cat_info.get('deductible') else 0

    return {
        'category': best_category,
        'deductible': cat_info.get('deductible', False),
        'deduction_rate': deduction_rate,
        'deductible_amount': abs(amount) * deduction_rate if cat_info.get('deductible') else 0,
        'irs_line': cat_info.get('irs_line', 'N/A'),
        'hmrc_category': cat_info.get('hmrc_category', 'N/A'),
        'confidence': min(100, best_score * 10) if best_score > 0 else 30,
    }


def categorize_batch(transactions):
    """Categorize a list of transactions.

    Each transaction: {'date': '...', 'description': '...', 'amount': float}
    Returns enriched list with category info.
    """
    results = []
    for txn in transactions:
        cat = categorize_transaction(
            txn.get('description', ''),
            txn.get('amount', 0)
        )
        results.append({**txn, **cat})
    return results


def generate_summary(categorized_transactions, tax_country='US'):
    """Generate financial summary from categorized transactions."""
    summary = {
        'total_income': 0,
        'total_expenses': 0,
        'total_deductible': 0,
        'total_non_deductible': 0,
        'net_profit': 0,
        'category_breakdown': {},
        'monthly_breakdown': {},
        'tax_country': tax_country,
    }

    for txn in categorized_transactions:
        amount = abs(txn.get('amount', 0))
        category = txn.get('category', 'uncategorized')
        deductible_amt = txn.get('deductible_amount', 0)
        date_str = txn.get('date', '')

        # Parse month
        month = 'Unknown'
        try:
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']:
                try:
                    dt = datetime.strptime(str(date_str)[:10], fmt)
                    month = dt.strftime('%Y-%m')
                    break
                except ValueError:
                    continue
        except Exception:
            pass

        if category == 'income' or txn.get('amount', 0) > 0:
            summary['total_income'] += amount
        elif category != 'transfer':
            summary['total_expenses'] += amount

        if txn.get('deductible'):
            summary['total_deductible'] += deductible_amt
        elif category not in ('income', 'transfer'):
            summary['total_non_deductible'] += amount

        # Category breakdown
        if category not in summary['category_breakdown']:
            summary['category_breakdown'][category] = {
                'count': 0, 'total': 0, 'deductible': 0
            }
        summary['category_breakdown'][category]['count'] += 1
        summary['category_breakdown'][category]['total'] += amount
        summary['category_breakdown'][category]['deductible'] += deductible_amt

        # Monthly breakdown
        if month not in summary['monthly_breakdown']:
            summary['monthly_breakdown'][month] = {'income': 0, 'expenses': 0}
        if category == 'income':
            summary['monthly_breakdown'][month]['income'] += amount
        elif category != 'transfer':
            summary['monthly_breakdown'][month]['expenses'] += amount

    summary['net_profit'] = summary['total_income'] - summary['total_expenses']
    return summary
