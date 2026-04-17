"""
Tax Calculator — US (1099/Schedule C) + UK (Self-Assessment)
Estimates quarterly/yearly taxes for freelancers.
"""

from app.config import (
    US_TAX_BRACKETS_2026, US_SELF_EMPLOYMENT_TAX_RATE,
    US_STANDARD_DEDUCTION_2026, UK_TAX_BRACKETS_2026,
    UK_NI_CLASS2_WEEKLY, UK_NI_CLASS4_LOWER, UK_NI_CLASS4_RATE,
)


def calculate_us_tax(net_profit, filing_status='single'):
    """Calculate US federal tax for self-employed freelancer."""
    if net_profit <= 0:
        return {
            'taxable_income': 0, 'federal_tax': 0,
            'self_employment_tax': 0, 'total_tax': 0,
            'effective_rate': 0, 'quarterly_estimate': 0,
        }

    # Self-employment tax (Social Security + Medicare)
    se_taxable = net_profit * 0.9235  # 92.35% of net
    se_tax = se_taxable * US_SELF_EMPLOYMENT_TAX_RATE
    se_deduction = se_tax * 0.5  # Can deduct half

    # Taxable income
    taxable = net_profit - se_deduction - US_STANDARD_DEDUCTION_2026
    taxable = max(0, taxable)

    # Federal income tax (progressive brackets)
    federal_tax = 0
    prev_limit = 0
    for limit, rate in US_TAX_BRACKETS_2026:
        if taxable <= 0:
            break
        bracket_income = min(taxable, limit - prev_limit)
        federal_tax += bracket_income * rate
        taxable -= bracket_income
        prev_limit = limit

    total_tax = federal_tax + se_tax
    effective_rate = (total_tax / net_profit * 100) if net_profit > 0 else 0

    return {
        'net_profit': round(net_profit, 2),
        'se_taxable_income': round(se_taxable, 2),
        'self_employment_tax': round(se_tax, 2),
        'se_deduction': round(se_deduction, 2),
        'standard_deduction': US_STANDARD_DEDUCTION_2026,
        'taxable_income': round(max(0, net_profit - se_deduction - US_STANDARD_DEDUCTION_2026), 2),
        'federal_income_tax': round(federal_tax, 2),
        'total_tax': round(total_tax, 2),
        'effective_rate': round(effective_rate, 1),
        'quarterly_estimate': round(total_tax / 4, 2),
        'country': 'US',
        'disclaimer': 'Estimate only. Consult a tax professional for accurate filing.',
    }


def calculate_uk_tax(net_profit):
    """Calculate UK tax for self-employed (self-assessment)."""
    if net_profit <= 0:
        return {
            'taxable_income': 0, 'income_tax': 0,
            'ni_class2': 0, 'ni_class4': 0,
            'total_tax': 0, 'effective_rate': 0,
        }

    # Income tax (progressive brackets)
    income_tax = 0
    remaining = net_profit
    prev_limit = 0
    for limit, rate in UK_TAX_BRACKETS_2026:
        if remaining <= 0:
            break
        bracket = min(remaining, limit - prev_limit)
        income_tax += bracket * rate
        remaining -= bracket
        prev_limit = limit

    # National Insurance Class 2 (flat weekly)
    ni_class2 = UK_NI_CLASS2_WEEKLY * 52

    # National Insurance Class 4
    ni_class4 = 0
    if net_profit > UK_NI_CLASS4_LOWER:
        ni_class4 = (net_profit - UK_NI_CLASS4_LOWER) * UK_NI_CLASS4_RATE

    total_tax = income_tax + ni_class2 + ni_class4
    effective_rate = (total_tax / net_profit * 100) if net_profit > 0 else 0

    return {
        'net_profit': round(net_profit, 2),
        'personal_allowance': 12570,
        'taxable_income': round(max(0, net_profit - 12570), 2),
        'income_tax': round(income_tax, 2),
        'ni_class2': round(ni_class2, 2),
        'ni_class4': round(ni_class4, 2),
        'total_tax': round(total_tax, 2),
        'effective_rate': round(effective_rate, 1),
        'quarterly_payment_on_account': round(total_tax / 2, 2),
        'country': 'UK',
        'disclaimer': 'Estimate only. Consult HMRC or an accountant for accurate assessment.',
    }


def calculate_tax(net_profit, country='US'):
    if country.upper() == 'UK':
        return calculate_uk_tax(net_profit)
    return calculate_us_tax(net_profit)
