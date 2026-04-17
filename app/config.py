"""App configuration — loads from .env"""
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
APP_URL = os.getenv("APP_URL", "http://localhost:8000")

# Tax rules
US_TAX_BRACKETS_2026 = [
    (11600, 0.10),
    (47150, 0.12),
    (100525, 0.22),
    (191950, 0.24),
    (243725, 0.32),
    (609350, 0.35),
    (float('inf'), 0.37),
]

US_SELF_EMPLOYMENT_TAX_RATE = 0.153  # 15.3%
US_STANDARD_DEDUCTION_2026 = 15000

UK_TAX_BRACKETS_2026 = [
    (12570, 0.0),    # Personal allowance
    (50270, 0.20),   # Basic rate
    (125140, 0.40),  # Higher rate
    (float('inf'), 0.45),  # Additional rate
]

UK_NI_CLASS2_WEEKLY = 3.45
UK_NI_CLASS4_LOWER = 12570
UK_NI_CLASS4_RATE = 0.06
