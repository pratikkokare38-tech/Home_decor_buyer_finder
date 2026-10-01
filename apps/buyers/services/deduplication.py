from typing import List, Dict
from apps.core.utils import normalize_domain, clean_email

class DeduplicationService:
    """
    Deduplicates buyer items by normalized domain, then by business name + city.
    """
    @classmethod
    def deduplicate(cls, buyers: List[Dict]) -> List[Dict]:
        seen_domains = set()
        seen_emails = set()
        seen_names = set()
        unique_buyers = []

        for b in buyers:
            email = clean_email(b.get('email', ''))
            domain = normalize_domain(b.get('website', '')) or b.get('domain', '')
            name_key = f"{b.get('business_name', '').lower().strip()}:{b.get('city', '').lower().strip()}"

            if email and email in seen_emails:
                continue
            if domain and domain in seen_domains:
                continue
            if name_key in seen_names:
                continue

            if email:
                seen_emails.add(email)
            if domain:
                seen_domains.add(domain)
            seen_names.add(name_key)

            unique_buyers.append(b)

        return unique_buyers
