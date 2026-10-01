from typing import Dict, Tuple
from integrations.website_crawler import WebsiteCrawlerClient
from integrations.hunter import HunterClient
from apps.buyers.services.verification_service import VerificationService
from apps.core.utils import clean_email, normalize_domain


class EmailFinderService:
    """
    Orchestrates layered email discovery (Map Data -> Website Crawler -> Hunter.io)
    followed by local MX verification.
    """
    def __init__(self):
        self.crawler = WebsiteCrawlerClient()
        self.hunter = HunterClient()

    def discover_email(self, buyer_dict: Dict) -> Dict:
        """
        Find and verify the best contact email for a buyer entry.
        Modifies buyer_dict with email, email_source, and email_status.
        """
        email = clean_email(buyer_dict.get('email', ''))
        source = buyer_dict.get('email_source', '')

        # Layer 1: Map Data Email
        if email:
            status, _ = VerificationService.verify(email)
            buyer_dict['email'] = email
            buyer_dict['email_source'] = 'map_data'
            buyer_dict['email_status'] = status
            return buyer_dict

        website = buyer_dict.get('website', '')
        domain = buyer_dict.get('domain') or normalize_domain(website)

        # Layer 2: Own Website Contact Page Scraper
        if website:
            crawled_emails = self.crawler.find_emails(website)
            if crawled_emails:
                best_email = crawled_emails[0]
                status, _ = VerificationService.verify(best_email)
                buyer_dict['email'] = best_email
                buyer_dict['email_source'] = 'crawler'
                buyer_dict['email_status'] = status
                return buyer_dict

        # Layer 3: Hunter.io Domain Search (Only if Layer 1 & 2 found nothing)
        if domain:
            try:
                hunter_emails = self.hunter.domain_search(domain, limit=1)
                if hunter_emails:
                    best_email = hunter_emails[0]['email']
                    status, _ = VerificationService.verify(best_email)
                    buyer_dict['email'] = best_email
                    buyer_dict['email_source'] = 'hunter'
                    buyer_dict['email_status'] = status
                    return buyer_dict
            except Exception:
                pass

        buyer_dict['email'] = ""
        buyer_dict['email_source'] = 'none'
        buyer_dict['email_status'] = 'invalid'
        return buyer_dict
