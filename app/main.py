"""
FreelanceBooks AI — AI Bookkeeping + Tax Prep for Freelancers
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

app = FastAPI(
    title="FreelanceBooks AI",
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
    return {"status": "ok", "service": "FreelanceBooks AI"}


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
