import re
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from apps.core.utils import clean_email, generate_cache_key
from apps.core.models import ApiCache


class WebsiteCrawlerClient:
    """
    Layer 2 Email Finder: Custom contact page web scraper.
    Extracts contact emails directly from buyer websites safely & ethically.
    """
    TIMEOUT = 3  # seconds timeout
    MAX_PAGES = 2
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DecorFinderBot/1.0 (+http://homedecorbuyerfinder.com)"
    
    # Regex to extract valid emails while ignoring image filenames & common false positives
    EMAIL_REGEX = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    )
    EXCLUDE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.pdf', '.css', '.js')

    def find_emails(self, website_url: str) -> List[str]:
        """
        Crawl website homepage and contact pages to discover contact email addresses.
        """
        if not website_url:
            return []

        if not website_url.startswith(('http://', 'https://')):
            website_url = 'http://' + website_url

        cache_key = generate_cache_key("crawl_email", {"url": website_url})
        cached = ApiCache.objects.filter(cache_key=cache_key).first()
        if cached and cached.is_valid():
            return cached.response_data

        discovered_emails = set()
        pages_to_crawl = [website_url]
        visited_urls = set()

        headers = {"User-Agent": self.USER_AGENT}

        try:
            # 1. Fetch homepage first
            resp = requests.get(website_url, headers=headers, timeout=self.TIMEOUT)
            visited_urls.add(website_url)

            if resp.status_code == 200:
                html = resp.text
                discovered_emails.update(self._extract_emails_from_text(html))

                # 2. Find contact or about links on homepage
                soup = BeautifulSoup(html, 'lxml')
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href'].strip()
                    if href.startswith('mailto:'):
                        mail = href.replace('mailto:', '').split('?')[0].strip()
                        if self._is_valid_candidate_email(mail):
                            discovered_emails.add(clean_email(mail))
                    else:
                        full_link = urljoin(website_url, href)
                        parsed_link = urlparse(full_link)
                        parsed_home = urlparse(website_url)

                        # Only follow links on same domain matching contact keywords
                        if parsed_link.netloc == parsed_home.netloc and full_link not in visited_urls:
                            path_lower = parsed_link.path.lower()
                            if any(k in path_lower for k in ['contact', 'about', 'team', 'connect', 'touch', 'help']):
                                if full_link not in pages_to_crawl and len(pages_to_crawl) < self.MAX_PAGES:
                                    pages_to_crawl.append(full_link)

            # 3. Crawl remaining contact subpages
            for page_url in pages_to_crawl[1:]:
                if page_url in visited_urls:
                    continue
                visited_urls.add(page_url)
                try:
                    sub_resp = requests.get(page_url, headers=headers, timeout=self.TIMEOUT)
                    if sub_resp.status_code == 200:
                        discovered_emails.update(self._extract_emails_from_text(sub_resp.text))
                except Exception:
                    continue

        except Exception:
            pass  # Fail gracefully if site is offline or blocks request

        final_emails = [e for e in list(discovered_emails) if self._is_valid_candidate_email(e)]
        
        # Rank candidate emails: prefer info@, sales@, hello@, contact@ over generic emails
        final_emails.sort(key=lambda e: 0 if any(e.startswith(p) for p in ['info@', 'sales@', 'hello@', 'contact@', 'buyer@', 'orders@']) else 1)

        # Cache result for 30 days
        ApiCache.set_cache(cache_key, "crawler", final_emails, ttl_days=30)

        return final_emails

    def _extract_emails_from_text(self, text: str) -> set:
        raw_matches = self.EMAIL_REGEX.findall(text)
        return {clean_email(m) for m in raw_matches if self._is_valid_candidate_email(m)}

    def _is_valid_candidate_email(self, email: str) -> bool:
        if not email or '@' not in email:
            return False
        email_lower = email.lower()
        if any(email_lower.endswith(ext) for ext in self.EXCLUDE_EXTENSIONS):
            return False
        if any(bad in email_lower for bad in ['example.com', 'domain.com', 'sentry.io', 'schema.org', 'w3.org', 'noreply', 'no-reply']):
            return False
        return True
