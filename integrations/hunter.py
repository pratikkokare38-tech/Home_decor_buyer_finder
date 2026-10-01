import datetime
from typing import Dict, List, Optional
from django.conf import settings
from django.utils import timezone

from integrations.base import BaseAPIClient
from integrations.exceptions import QuotaExceededError
from apps.core.models import ApiCache, ApiUsage
from apps.core.utils import generate_cache_key, clean_email


class HunterClient(BaseAPIClient):
    """
    Hunter.io Domain Search & Email Verification API Client (Layer 3 Fallback).
    Strictly checks monthly quota budget (50 free credits/month) before executing network calls.
    """
    def __init__(self):
        super().__init__(base_url="https://api.hunter.io/v2")
        self.api_key = settings.HUNTER_API_KEY
        self.monthly_budget = settings.HUNTER_MONTHLY_BUDGET

    def domain_search(self, domain: str, limit: int = 2) -> List[Dict]:
        """
        Search for emails associated with a domain name on Hunter.io.
        Consumes 1 credit.
        """
        if not domain:
            return []

        cache_key = generate_cache_key("hunter_domain", {"domain": domain, "limit": limit})
        cached = ApiCache.objects.filter(cache_key=cache_key).first()
        if cached and cached.is_valid():
            return cached.response_data

        if not self.api_key:
            return []

        # Check monthly budget before calling Hunter API
        used_credits = ApiUsage.get_monthly_credits("hunter")
        if used_credits >= self.monthly_budget:
            raise QuotaExceededError("Hunter.io monthly credit quota budget reached (50/50).")

        params = {
            "domain": domain,
            "limit": limit,
            "api_key": self.api_key
        }

        try:
            response = self.request("GET", "/domain-search", params=params)
            data = response.json()
            ApiUsage.record_usage("hunter", credits=1)

            emails = []
            for item in data.get("data", {}).get("emails", []):
                value = clean_email(item.get("value", ""))
                if value:
                    emails.append({
                        "email": value,
                        "first_name": item.get("first_name", ""),
                        "last_name": item.get("last_name", ""),
                        "position": item.get("position", ""),
                        "confidence": item.get("confidence", 0)
                    })

            # Cache for 30 days
            expires_at = timezone.now() + datetime.timedelta(days=30)
            ApiCache.objects.create(
                cache_key=cache_key,
                provider="hunter",
                response_data=emails,
                expires_at=expires_at
            )

            return emails

        except QuotaExceededError:
            raise
        except Exception:
            return []

    def verify_email(self, email: str) -> Optional[Dict]:
        """
        Verify single email address validity via Hunter Email Verifier.
        Consumes 0.5 credits.
        """
        if not email:
            return None

        cache_key = generate_cache_key("hunter_verify", {"email": email})
        cached = ApiCache.objects.filter(cache_key=cache_key).first()
        if cached and cached.is_valid():
            return cached.response_data

        if not self.api_key:
            return None

        used_credits = ApiUsage.get_monthly_credits("hunter")
        if used_credits >= self.monthly_budget:
            return None

        params = {
            "email": email,
            "api_key": self.api_key
        }

        try:
            response = self.request("GET", "/email-verifier", params=params)
            data = response.json()
            ApiUsage.record_usage("hunter", credits=1)

            result_data = data.get("data", {})
            result = {
                "status": result_data.get("status"),  # valid, accept_all, webmail, disposable, invalid
                "score": result_data.get("score"),
                "regexp": result_data.get("regexp"),
                "mx_records": result_data.get("mx_records"),
                "smtp_check": result_data.get("smtp_check")
            }

            # Cache verification result for 30 days
            expires_at = timezone.now() + datetime.timedelta(days=30)
            ApiCache.objects.create(
                cache_key=cache_key,
                provider="hunter",
                response_data=result,
                expires_at=expires_at
            )

            return result

        except Exception:
            return None
