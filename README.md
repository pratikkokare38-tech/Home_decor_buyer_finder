# Home Decor Buyer Finder (USA)

A full-stack Django + DRF web application designed for **US Home Decor Sellers, Artisans, and Wholesale Distributors** to automatically discover verified buyers (retail stores, interior designers, gift shops, furniture showrooms) using **live free APIs** and dispatch compliance-checked pitch email campaigns.

---

## 🌟 Key Features

1. **Strict NO-CSV Policy**: All buyer leads are discovered dynamically through live geolocation & place search APIs.
2. **Multi-Source Discovery Pipeline**:
   - **Geoapify Geocoding & Places API** (Primary layer for US business discovery).
   - **OpenStreetMap Overpass API** (Free fallback layer for furniture & decor shops).
   - **Custom Contact Page Scraper** (Ethical Layer 2 crawler searching website contact pages & mailto tags).
   - **Hunter.io Domain Search** (Layer 3 fallback with strict monthly credit budget checks).
3. **Local Email Verification**: Validates regex syntax, filters disposable email domains, and runs `dnspython` MX record checks.
4. **CAN-SPAM Compliant Pitch Campaigns**:
   - Automatic inclusion of seller's physical postal address in footers.
   - One-click unsubscribe opt-out links (`/unsubscribe/?email=...`).
   - Daily rate-limit batching (300 emails/day max on Brevo free tier).
5. **Modern Dark Glassmorphic UI**: HTML5 + Vanilla CSS + Vanilla JS (`fetch` + CSRF headers).

---

## 🛠️ Architecture & Tech Stack

```
homedecor_buyer_finder/
├── config/                  # Django Settings (base.py, dev.py, prod.py)
├── apps/
│   ├── core/                # ApiCache, ApiUsage, Constants, Utils
│   ├── accounts/            # User Auth & SellerProfile
│   ├── buyers/              # SearchQuery, Buyer models & Discovery Pipeline
│   └── campaigns/           # EmailTemplate, Campaign, EmailLog & Unsubscribe
├── integrations/            # BaseAPIClient, Geoapify, Overpass, Crawler, Hunter, EmailSender
├── templates/               # HTML5 Templates (Glassmorphism design)
├── static/                  # Modular CSS & JS (api.js, search.js, results.js, campaign.js)
└── tests/                   # Pytest test suite with mocked HTTP (responses)
```

---

## 🚀 Quick Setup & Installation

### 1. Clone & Setup Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and set your API keys:
```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_SETTINGS_MODULE=config.settings.dev

GEOAPIFY_API_KEY=your_geoapify_key
HUNTER_API_KEY=your_hunter_key

EMAIL_PROVIDER=console
BREVO_API_KEY=your_brevo_key
RESEND_API_KEY=your_resend_key
```

### 4. Database Migrations
```bash
python manage.py migrate
```

### 5. Run Development Server
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Unit Tests

Run the pytest test suite:
```bash
pytest
```

---

## 📜 Free API Quotas & Limits

| API Provider | Role | Free Tier Allowance | Quota Enforcement |
|---|---|---|---|
| **Geoapify** | Geocoding & Places Search | 3,000 credits/day | Cached for 7-30 days |
| **OpenStreetMap** | Fallback Places Search | Unlimited (Free) | Rate throttled & cached |
| **Hunter.io** | Domain Email Search | 50 credits/month | Pre-call budget check |
| **Brevo** | Transactional Pitch Email | 300 emails/day | Daily batch throttling |

---

## ⚖️ Legal & Compliance Note (CAN-SPAM)
All emails sent through DecorFinder adhere to the US CAN-SPAM Act:
1. Truthful From lines and non-deceptive subject lines.
2. Mandatory inclusion of the seller's physical postal address.
3. Automatic opt-out / unsubscribe links on all pitch footers.
4. Immediate exclusion of unsubscribed email addresses.
