"""
BooksBird — AI Bookkeeping + Tax Prep for Freelancers
Upload bank CSV → AI categorizes expenses → Tax estimate ready

100% free to run. FastAPI + Supabase + Stripe.
"""

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

from app.services.csv_parser import parse_csv
from app.services.categorizer import categorize_batch, generate_summary
from app.services.tax_calculator import calculate_tax
from app.services.report_generator import generate_full_report
from app.services.invoice_generator import create_invoice
from app.services.pnl_generator import generate_pnl

app = FastAPI(
    title="BooksBird",
    description="AI-powered bookkeeping + tax prep for freelancers",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates + Static
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "ok", "service": "BooksBird"}


@app.post("/api/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    country: str = Form("US"),
):
    """Upload bank CSV → get categorized transactions + tax estimate."""
    # Validate file
    if not file.filename:
        raise HTTPException(400, "No file provided")

    allowed_types = ['.csv', '.CSV']
    ext = os.path.splitext(file.filename)[1]
    if ext not in allowed_types:
        raise HTTPException(400, f"Only CSV files accepted. Got: {ext}")

    # Read file (with size limit)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large. Max 10 MB.")

    if len(content) == 0:
        raise HTTPException(400, "Empty file")

    try:
        # Parse CSV
        transactions = parse_csv(content, file.filename)

        # AI Categorize
        categorized = categorize_batch(transactions)

        # Generate report
        report = generate_full_report(categorized, country.upper())

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "transactions": categorized,
            "summary": report['summary'],
            "tax_estimate": report['tax_estimate'],
            "transaction_count": report['transaction_count'],
        })
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)[:200]}")


@app.post("/api/report/text")
async def text_report(
    file: UploadFile = File(...),
    country: str = Form("US"),
):
    """Get plain text report (accountant-ready)."""
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")

    transactions = parse_csv(content)
    categorized = categorize_batch(transactions)
    report = generate_full_report(categorized, country.upper())
    return PlainTextResponse(report['text_report'])


@app.post("/api/report/csv")
async def csv_report(
    file: UploadFile = File(...),
    country: str = Form("US"),
):
    """Get categorized CSV export."""
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")

    transactions = parse_csv(content)
    categorized = categorize_batch(transactions)
    report = generate_full_report(categorized, country.upper())

    return PlainTextResponse(
        report['csv_export'],
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=freelancebooks_export.csv"}
    )


@app.post("/api/tax-estimate")
async def tax_estimate(
    income: float = Form(...),
    expenses: float = Form(0),
    country: str = Form("US"),
):
    """Quick tax estimate without CSV upload."""
    net_profit = income - expenses
    tax = calculate_tax(net_profit, country.upper())
    return JSONResponse({"success": True, "tax_estimate": tax})


@app.post("/api/invoice")
async def generate_invoice(request: Request):
    """Generate professional invoice."""
    data = await request.json()
    if not data.get('items'):
        raise HTTPException(400, "At least one line item required")
    invoice = create_invoice(data)
    return HTMLResponse(invoice['html'])


@app.post("/api/pnl")
async def profit_loss(
    file: UploadFile = File(...),
    country: str = Form("US"),
):
    """Generate Profit & Loss statement."""
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")
    transactions = parse_csv(content)
    categorized = categorize_batch(transactions)
    pnl = generate_pnl(categorized)
    return PlainTextResponse(pnl['text'])


@app.post("/api/tax-savings-tips")
async def tax_savings(
    file: UploadFile = File(...),
    country: str = Form("US"),
):
    """AI-powered tax savings tips based on your expenses."""
    content = await file.read()
    transactions = parse_csv(content)
    categorized = categorize_batch(transactions)
    summary = generate_summary(categorized, country.upper())

    tips = []
    cats = summary.get('category_breakdown', {})

    # Tip 1: Home office
    if 'rent_office' not in cats:
        tips.append({
            'tip': 'Claim Home Office Deduction',
            'savings': '$1,500-5,000/year',
            'detail': 'If you work from home, deduct a portion of rent/mortgage, utilities, and internet. IRS allows simplified method ($5/sq ft, max 300 sq ft = $1,500).',
        })

    # Tip 2: Phone & internet
    phone = cats.get('phone_internet', {})
    if phone.get('total', 0) > 0 and phone.get('deductible', 0) < phone.get('total', 0):
        tips.append({
            'tip': 'Increase Phone/Internet Deduction',
            'savings': f"${phone['total'] * 0.3:,.0f}/year more",
            'detail': 'Track business vs personal usage %. Most freelancers can deduct 50-80% of phone/internet bills.',
        })

    # Tip 3: Retirement
    tips.append({
        'tip': 'Open SEP-IRA (Save on taxes + retirement)',
        'savings': 'Up to $69,000/year deduction',
        'detail': 'Self-employed can contribute up to 25% of net income to SEP-IRA. Reduces taxable income significantly.',
    })

    # Tip 4: Health insurance
    if 'insurance' not in cats:
        tips.append({
            'tip': 'Deduct Health Insurance Premiums',
            'savings': '$3,000-12,000/year',
            'detail': 'Self-employed health insurance premiums are 100% deductible above-the-line.',
        })

    # Tip 5: Equipment
    if 'equipment' not in cats:
        tips.append({
            'tip': 'Section 179 — Deduct Equipment Purchases',
            'savings': 'Up to $1,220,000 deduction',
            'detail': 'Laptop, phone, camera, monitors — deduct full price in the year of purchase (Section 179).',
        })

    # Tip 6: Meals
    meals = cats.get('meals_entertainment', {})
    if meals.get('total', 0) > 0:
        tips.append({
            'tip': 'Document Business Meals Better',
            'savings': f"${meals['total'] * 0.5:,.0f}/year",
            'detail': 'Keep receipts + note who you met and business purpose. 50% of business meals are deductible.',
        })

    # Tip 7: Education
    if 'education_training' not in cats or cats['education_training']['total'] < 500:
        tips.append({
            'tip': 'Invest in Professional Development',
            'savings': '$500-5,000/year deduction',
            'detail': 'Courses, certifications, conferences, books — all deductible if related to your business.',
        })

    # Tip 8: Mileage
    transport = cats.get('car_transport', {})
    if transport.get('total', 0) > 0:
        tips.append({
            'tip': 'Track Mileage Instead of Actual Expenses',
            'savings': f"${transport['total'] * 0.5:,.0f} more/year",
            'detail': 'IRS standard mileage rate = $0.70/mile (2026). Often higher deduction than actual gas costs.',
        })

    total_potential = sum(
        float(t['savings'].replace('$', '').replace(',', '').split('/')[0].split('-')[0])
        for t in tips if '$' in t['savings']
    )

    return JSONResponse({
        'success': True,
        'tips_count': len(tips),
        'estimated_total_savings': f"${total_potential:,.0f}+/year",
        'tips': tips,
    })




# ═══════════════════════════════════════════
# Invoice Chaser Tool (PayChase)
# ═══════════════════════════════════════════
from app.services.ai_reminder import generate_reminder, generate_sequence
from app.services.payment_scorer import score_client, generate_cashflow_forecast
from app.services.late_fee_calculator import calculate_late_fee


@app.get("/invoices", response_class=HTMLResponse)
async def invoices_page(request: Request):
    return templates.TemplateResponse("invoices.html", {"request": request})


@app.post("/api/reminder")
async def reminder_api(request: Request):
    data = await request.json()
    if not data.get('invoice_no') or not data.get('amount'):
        raise HTTPException(400, "invoice_no and amount required")
    r = generate_reminder(data, sender_name=data.get('sender_name', ''))
    return JSONResponse({"success": True, "reminder": r})


@app.post("/api/sequence")
async def sequence_api(request: Request):
    data = await request.json()
    if not data.get('invoice_no') or not data.get('amount'):
        raise HTTPException(400, "invoice_no and amount required")
    s = generate_sequence(data, sender_name=data.get('sender_name', ''))
    return JSONResponse({"success": True, "sequence_count": len(s), "sequence": s})


@app.post("/api/score-client")
async def score_api(request: Request):
    data = await request.json()
    score = score_client(data.get('payment_history', []))
    return JSONResponse({"success": True, "client_name": data.get('client_name', ''), "score": score})


@app.post("/api/late-fee")
async def latefee_api(request: Request):
    data = await request.json()
    if not data.get('amount') or not data.get('due_date'):
        raise HTTPException(400, "amount and due_date required")
    fee = calculate_late_fee(data['amount'], data['due_date'], rate_monthly=data.get('rate', 1.5))
    return JSONResponse({"success": True, "late_fee": fee})


@app.post("/api/forecast")
async def forecast_api(request: Request):
    data = await request.json()
    forecast = generate_cashflow_forecast(data.get('invoices', []))
    return JSONResponse({"success": True, "forecast": forecast})
