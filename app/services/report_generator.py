"""
Report Generator — creates tax-ready reports for freelancers.
Outputs: JSON summary, CSV export, text report.
"""

import csv
import io
from datetime import datetime
from .tax_calculator import calculate_tax


def generate_text_report(summary, tax_info, transactions):
    """Generate human-readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("  FreelanceBooks AI — Financial Report")
    lines.append(f"  Generated: {datetime.now().strftime('%B %d, %Y')}")
    lines.append(f"  Tax Country: {summary.get('tax_country', 'US')}")
    lines.append("=" * 60)

    lines.append("\n--- INCOME & EXPENSES ---")
    lines.append(f"  Total Income:           ${summary['total_income']:>12,.2f}")
    lines.append(f"  Total Expenses:         ${summary['total_expenses']:>12,.2f}")
    lines.append(f"  Net Profit:             ${summary['net_profit']:>12,.2f}")

    lines.append(f"\n  Total Deductible:       ${summary['total_deductible']:>12,.2f}")
    lines.append(f"  Non-Deductible:         ${summary['total_non_deductible']:>12,.2f}")

    lines.append("\n--- CATEGORY BREAKDOWN ---")
    for cat, info in sorted(summary['category_breakdown'].items(),
                             key=lambda x: x[1]['total'], reverse=True):
        if info['total'] > 0:
            ded = f"  (deductible: ${info['deductible']:,.2f})" if info['deductible'] > 0 else ""
            lines.append(f"  {cat:30s}  ${info['total']:>10,.2f}  ({info['count']} txns){ded}")

    lines.append("\n--- MONTHLY BREAKDOWN ---")
    for month in sorted(summary['monthly_breakdown'].keys()):
        m = summary['monthly_breakdown'][month]
        profit = m['income'] - m['expenses']
        lines.append(f"  {month}:  Income ${m['income']:>10,.2f}  "
                      f"Expenses ${m['expenses']:>10,.2f}  "
                      f"Profit ${profit:>10,.2f}")

    lines.append("\n--- TAX ESTIMATE ---")
    if tax_info.get('country') == 'UK':
        lines.append(f"  Income Tax:             £{tax_info.get('income_tax', 0):>12,.2f}")
        lines.append(f"  NI Class 2:             £{tax_info.get('ni_class2', 0):>12,.2f}")
        lines.append(f"  NI Class 4:             £{tax_info.get('ni_class4', 0):>12,.2f}")
        lines.append(f"  Total Tax:              £{tax_info.get('total_tax', 0):>12,.2f}")
        lines.append(f"  Effective Rate:          {tax_info.get('effective_rate', 0)}%")
        lines.append(f"  Payment on Account:     £{tax_info.get('quarterly_payment_on_account', 0):>12,.2f}")
    else:
        lines.append(f"  Federal Income Tax:     ${tax_info.get('federal_income_tax', 0):>12,.2f}")
        lines.append(f"  Self-Employment Tax:    ${tax_info.get('self_employment_tax', 0):>12,.2f}")
        lines.append(f"  Total Estimated Tax:    ${tax_info.get('total_tax', 0):>12,.2f}")
        lines.append(f"  Effective Rate:          {tax_info.get('effective_rate', 0)}%")
        lines.append(f"  Quarterly Payment:      ${tax_info.get('quarterly_estimate', 0):>12,.2f}")

    lines.append(f"\n  {tax_info.get('disclaimer', '')}")
    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


def generate_csv_export(transactions):
    """Generate CSV export of categorized transactions."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Date', 'Description', 'Amount', 'Category',
        'Deductible', 'Deductible Amount', 'IRS Line',
        'HMRC Category', 'Confidence'
    ])

    for txn in transactions:
        writer.writerow([
            txn.get('date', ''),
            txn.get('description', ''),
            txn.get('amount', 0),
            txn.get('category', ''),
            'Yes' if txn.get('deductible') else 'No',
            round(txn.get('deductible_amount', 0), 2),
            txn.get('irs_line', ''),
            txn.get('hmrc_category', ''),
            txn.get('confidence', 0),
        ])

    return output.getvalue()


def generate_full_report(categorized_transactions, tax_country='US'):
    """Generate complete report: summary + tax + text + CSV."""
    from .categorizer import generate_summary

    summary = generate_summary(categorized_transactions, tax_country)
    tax_info = calculate_tax(summary['net_profit'], tax_country)
    text_report = generate_text_report(summary, tax_info, categorized_transactions)
    csv_export = generate_csv_export(categorized_transactions)

    return {
        'summary': summary,
        'tax_estimate': tax_info,
        'text_report': text_report,
        'csv_export': csv_export,
        'transaction_count': len(categorized_transactions),
        'generated_at': datetime.now().isoformat(),
    }
