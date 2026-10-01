import hashlib
import json
import re

def generate_cache_key(prefix: str, params: dict) -> str:
    """Generate a deterministic MD5 hash string for API response caching."""
    serialized = json.dumps(params, sort_keys=True)
    hash_str = hashlib.md5(serialized.encode('utf-8')).hexdigest()
    return f"{prefix}:{hash_str}"


def normalize_domain(url: str) -> str:
    """Extract clean domain name from URL string."""
    if not url:
        return ""
    url = url.strip().lower()
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    match = re.search(r'https?://(?:www\.)?([^/:]+)', url)
    return match.group(1) if match else ""


def clean_email(email: str) -> str:
    """Clean and normalize email address."""
    if not email:
        return ""
    return email.strip().lower()
