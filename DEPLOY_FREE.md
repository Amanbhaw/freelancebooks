# 🚀 FreelanceBooks AI — FREE Deployment + Payment Setup

## Complete FREE Stack:
- Hosting: Render.com (FREE forever)
- Payment: Stripe (FREE setup, 2.9% only when paid)
- Domain: FREE subdomain (freelancebooks.onrender.com)
- SSL: FREE (auto)
- Total cost: ₹0

---

## STEP 1: Deploy to Render (5 min)

1. Go to: https://render.com
2. Click "Get Started for Free" → Sign up with GitHub (Amanbhaw)
3. Click "New +" → "Web Service"
4. Select repo: "Amanbhaw/freelancebooks"
5. Settings:
   - Name: freelancebooks
   - Region: Oregon (Free)
   - Branch: master
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   - Plan: FREE
6. Click "Create Web Service"
7. Wait 2-3 min → Your URL: https://freelancebooks.onrender.com

---

## STEP 2: Add Stripe Payments (10 min)

### A. Create Stripe Account (FREE):
1. Go to: https://stripe.com
2. Sign up (email + password)
3. Skip business verification for now (use test mode)
4. Dashboard → Developers → API Keys
5. Copy: Publishable key (pk_test_...) + Secret key (sk_test_...)

### B. Create Stripe Pricing:
1. Stripe Dashboard → Products → "+ Add Product"
2. Product name: "FreelanceBooks AI Pro"
3. Pricing:
   - $29/month (recurring)
   - OR ₹999/month (INR)
4. Copy the Price ID (price_xxx...)

### C. Create Stripe Payment Link (EASIEST):
1. Stripe → Payment Links → Create
2. Select "FreelanceBooks AI Pro" product
3. Click "Create Link"
4. Copy the payment URL (https://buy.stripe.com/xxx)
5. This link = customers click → pay → done!

### D. Add to Render:
1. Render dashboard → freelancebooks → Environment
2. Add:
   - STRIPE_SECRET_KEY = sk_test_xxx
   - STRIPE_PUBLISHABLE_KEY = pk_test_xxx
3. Save → auto-redeploy

---

## STEP 3: Payment Flow (How Money Comes)

Customer journey:
1. Visits freelancebooks.onrender.com
2. Uses free (3 uploads/month)
3. Hits limit → "Upgrade to Pro" button
4. Clicks Stripe payment link
5. Pays $29/month (card/GPay/ApplePay)
6. Stripe collects → sends to YOUR bank
7. You get paid every week (auto-transfer)

Money flow:
  Customer pays $29
  → Stripe takes 2.9% + $0.30 = $1.14
  → YOU receive $27.86
  → Auto-deposit to your bank account weekly

---

## STEP 4: Stripe → Your Bank (FREE)

1. Stripe Dashboard → Settings → Payouts
2. Add bank account (IFSC + Account number)
3. Stripe sends ₹ to your bank every week
4. Minimum: $25 (₹2100) per payout
5. First payout: 7-14 days after first sale

---

## Revenue Calculator:

  5 customers × $29 = $145/mo (₹12,180)
  20 customers × $29 = $580/mo (₹48,720)
  50 customers × $29 = $1,450/mo (₹1,21,800)
  200 customers × $29 = $5,800/mo (₹4,87,200)

  Your cost: ₹0 forever (free hosting)
  Stripe fee: 2.9% (only from revenue)

---

## 💡 Marketing (FREE):

### Day 1: Reddit
Post in r/freelance, r/Upwork, r/solopreneur:
"Free beta: AI that auto-categorizes your expenses + estimates tax"

### Day 2: LinkedIn
"Built an AI tool that does what QuickBooks charges $30/mo for — free"

### Day 3: Product Hunt
Submit for launch → potential 1000+ visitors in 1 day

### Day 4: Indie Hackers
"Show IH: FreelanceBooks — AI bookkeeping for freelancers"

### Day 5+: Content
Blog: "How I saved $2000/year on accounting as a freelancer"
YouTube: Demo video (Loom free screen recording)
