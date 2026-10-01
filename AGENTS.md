Project: Django + DRF "Home Decor Buyer Finder" for US sellers.
Read project.md first and follow its folder structure exactly.

- Backend: Python, Django, DRF. Frontend: HTML, CSS, vanilla JS only.
- NEVER add CSV upload or CSV import. Buyers come only from live APIs.
- Use ONLY the free APIs in project.md Section 4. Do not add paid APIs or ones requiring a card.
- All external HTTP calls live in /integrations and inherit BaseAPIClient. No requests.get() anywhere else.
- Business logic goes in services/. Views stay thin.
- Read secrets from .env via python-decouple. Never hardcode or print keys.
- Every API call needs timeout, retry with backoff, error handling, caching, and usage tracking.
- Check API budget before calling Hunter. Prefer free layers first (map data, crawler, local checks).
- Deduplicate buyers by email and by domain.
- Only email valid addresses, skip unsubscribed ones, always add postal address and unsubscribe link.
- In dev settings, never send real emails.
- Sellers can only see their own searches, buyers, campaigns and logs.
- Write tests with mocked HTTP (responses library). Do not hit real APIs in tests.
- Work one phase at a time. Show a plan first, then implement, then summarize and wait.
- Comment non-obvious code; use type hints and docstrings on services and integrations.
