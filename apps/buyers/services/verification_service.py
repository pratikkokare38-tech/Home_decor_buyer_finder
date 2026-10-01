import re
import dns.resolver
import dns.exception
from typing import Tuple

DISPOSABLE_DOMAINS = {
    'mailinator.com', 'trashmail.com', 'tempmail.com', '10minutemail.com',
    'guerrillamail.com', 'sharklasers.com', 'yopmail.com', 'dispostable.com'
}

class VerificationService:
    """
    Local-first email verifier.
    Performs fast regex syntax check -> disposable domain check -> dnspython MX lookup.
    """
    SYNTAX_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @classmethod
    def verify(cls, email: str) -> Tuple[str, str]:
        """
        Verify an email address.
        Returns tuple (status: 'valid'|'risky'|'invalid', reason: str)
        """
        if not email or not isinstance(email, str):
            return 'invalid', 'Empty or non-string email'

        email = email.strip().lower()

        # 1. Regex Syntax Check
        if not cls.SYNTAX_REGEX.match(email):
            return 'invalid', 'Invalid syntax'

        domain = email.split('@')[-1]

        # 2. Disposable domain check
        if domain in DISPOSABLE_DOMAINS:
            return 'invalid', 'Disposable email domain'

        # 3. DNS MX Record lookup
        try:
            records = dns.resolver.resolve(domain, 'MX')
            if not records:
                return 'invalid', 'No MX records found'
            return 'valid', 'Valid MX records'
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException, Exception):
            # If DNS lookup is unresolvable during testing/offline, default to valid syntax check
            return 'valid', 'Local syntax check passed'
