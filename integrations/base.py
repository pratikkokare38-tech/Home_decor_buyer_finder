import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .exceptions import APIIntegrationError, RateLimitError, APIConnectionError


class BaseAPIClient:
    """
    Base HTTP Client for all external APIs.
    Enforces timeout, exponential retries, and unified error mapping.
    """
    DEFAULT_TIMEOUT = 12  # seconds
    DEFAULT_USER_AGENT = "DecorFinderBot/1.0 (+http://homedecorbuyerfinder.com; contact@homedecorbuyerfinder.com)"

    def __init__(self, base_url: str = "", retries: int = 3, backoff_factor: float = 0.5):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.DEFAULT_USER_AGENT})
        
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.DEFAULT_TIMEOUT

        try:
            response = self.session.request(method, url, **kwargs)
            if response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded for URL: {url}")
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout as err:
            raise APIConnectionError(f"Request timeout for {url}") from err
        except requests.exceptions.ConnectionError as err:
            raise APIConnectionError(f"Connection failed for {url}") from err
        except requests.exceptions.HTTPError as err:
            raise APIIntegrationError(f"HTTP error {response.status_code} for {url}: {response.text}") from err
        except Exception as err:
            raise APIIntegrationError(f"API request failed: {str(err)}") from err
