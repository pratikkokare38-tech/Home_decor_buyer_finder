import datetime
from typing import Dict, List, Optional
from django.conf import settings
from django.utils import timezone

from integrations.base import BaseAPIClient
from apps.core.models import ApiCache, ApiUsage
from apps.core.utils import generate_cache_key, normalize_domain
from apps.core.constants import BUYER_CATEGORIES


class GeoapifyClient(BaseAPIClient):
    """
    Geoapify Places & Geocoding API Client (Primary Discovery Layer).
    Falls back gracefully to OpenStreetMap Nominatim if no API key is provided or if the API call fails.
    """
    # Fallback coordinates for US state capitals / major hubs to ensure discovery always works
    STATE_COORDS = {
        'AL': (32.3770, -86.3006), 'AK': (58.3019, -134.4197), 'AZ': (33.4484, -112.0740),
        'AR': (34.7465, -92.2896), 'CA': (38.5816, -121.4944), 'CO': (39.7392, -104.9903),
        'CT': (41.7658, -72.6734), 'DE': (39.1582, -75.5244), 'FL': (30.4383, -84.2807),
        'GA': (33.7490, -84.3880), 'HI': (21.3069, -157.8583), 'ID': (43.6150, -116.2023),
        'IL': (39.7817, -89.6501), 'IN': (39.7684, -86.1581), 'IA': (41.5868, -93.6250),
        'KS': (39.0473, -95.6752), 'KY': (38.2009, -84.8733), 'LA': (30.4515, -91.1871),
        'ME': (44.3106, -69.7795), 'MD': (38.9784, -76.4922), 'MA': (42.3601, -71.0589),
        'MI': (42.7325, -84.5555), 'MN': (44.9537, -93.0900), 'MS': (32.2988, -90.1848),
        'MO': (38.5767, -92.1735), 'MT': (46.5891, -112.0391), 'NE': (40.8136, -96.7026),
        'NV': (39.1638, -119.7674), 'NH': (43.2081, -71.5376), 'NJ': (40.2206, -74.7597),
        'NM': (35.6870, -105.9378), 'NY': (42.6526, -73.7562), 'NC': (35.7796, -78.6382),
        'ND': (46.8083, -100.7837), 'OH': (39.9612, -82.9988), 'OK': (35.4676, -97.5164),
        'OR': (44.9429, -123.0351), 'PA': (40.2732, -76.8867), 'RI': (41.8240, -71.4128),
        'SC': (34.0007, -81.0348), 'SD': (44.3683, -100.3510), 'TN': (36.1627, -86.7816),
        'TX': (30.2672, -97.7431), 'UT': (40.7608, -111.8910), 'VT': (44.2601, -72.5754),
        'VA': (37.5407, -77.4360), 'WA': (47.0379, -122.9007), 'WV': (38.3498, -81.6326),
        'WI': (43.0731, -89.4012), 'WY': (41.1399, -104.8202), 'DC': (38.9072, -77.0369)
    }

    def __init__(self):
        super().__init__(base_url="https://api.geoapify.com")
        self.api_key = settings.GEOAPIFY_API_KEY

    def _geocode_nominatim(self, city: str, state: str) -> Optional[Dict]:
        """Free Nominatim geocoding fallback for US locations."""
        try:
            nom_resp = self.session.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": f"{city}, {state}, USA", "format": "json", "limit": 1},
                headers={"User-Agent": self.DEFAULT_USER_AGENT},
                timeout=8
            )
            if nom_resp.status_code == 200 and nom_resp.json():
                first = nom_resp.json()[0]
                return {
                    "lat": float(first["lat"]),
                    "lon": float(first["lon"]),
                    "city": city,
                    "state": state,
                    "formatted": first.get("display_name", f"{city}, {state}")
                }
        except Exception:
            pass
        return None

    def geocode(self, city: str, state: str, country: str = "US") -> Optional[Dict]:
        """
        Geocode a US city/state into latitude and longitude coordinates.
        Uses Geoapify primary with automatic fallback to OpenStreetMap Nominatim and major hub coords.
        """
        cache_key = generate_cache_key("geo_geocode", {"city": city.lower().strip(), "state": state.upper().strip(), "country": country})
        cached = ApiCache.objects.filter(cache_key=cache_key).first()
        if cached and cached.is_valid():
            return cached.response_data

        result = None

        # 1. Try Geoapify API if key configured
        if self.api_key:
            try:
                params = {
                    "city": city,
                    "state": state,
                    "country": country,
                    "apiKey": self.api_key
                }
                response = self.request("GET", "/v1/geocode/search", params=params, timeout=6)
                data = response.json()
                ApiUsage.record_usage("geoapify", credits=1)

                features = data.get("features", [])
                if features:
                    props = features[0].get("properties", {})
                    if props.get("lat") and props.get("lon"):
                        result = {
                            "lat": float(props["lat"]),
                            "lon": float(props["lon"]),
                            "city": props.get("city", city),
                            "state": props.get("state", state),
                            "formatted": props.get("formatted", f"{city}, {state}")
                        }
            except Exception:
                result = None

        # 2. Fallback to OpenStreetMap Nominatim
        if not result:
            result = self._geocode_nominatim(city, state)

        # 3. Fallback to State Major Hub Coordinates if city not geocoded
        if not result:
            state_upper = state.upper().strip()
            if state_upper in self.STATE_COORDS:
                lat, lon = self.STATE_COORDS[state_upper]
                result = {
                    "lat": lat,
                    "lon": lon,
                    "city": city,
                    "state": state_upper,
                    "formatted": f"{city}, {state_upper}, USA"
                }

        if result:
            ApiCache.set_cache(cache_key, "geocoding", result, ttl_days=30)
            return result

        return None

    def search_places(self, category: str, lat: float, lon: float, radius_km: int = 50, limit: int = 30) -> List[Dict]:
        """
        Search for home decor buyers near coordinates using Geoapify Places API.
        """
        cache_key = generate_cache_key("geo_places", {
            "category": category, "lat": round(lat, 3), "lon": round(lon, 3), "radius": radius_km, "limit": limit
        })
        cached = ApiCache.objects.filter(cache_key=cache_key).first()
        if cached and cached.is_valid():
            return cached.response_data

        if not self.api_key:
            return []

        cat_info = BUYER_CATEGORIES.get(category, BUYER_CATEGORIES['all'])
        geo_cat_str = ",".join(cat_info['geoapify_categories'])
        radius_meters = int(radius_km * 1000)

        params = {
            "categories": geo_cat_str,
            "filter": f"circle:{lon},{lat},{radius_meters}",
            "limit": limit,
            "apiKey": self.api_key
        }

        try:
            response = self.request("GET", "/v2/places", params=params, timeout=8)
            data = response.json()
            ApiUsage.record_usage("geoapify", credits=1)

            results = []
            for feature in data.get("features", []):
                props = feature.get("properties", {})
                name = props.get("name")
                if not name:
                    continue

                website = props.get("website", "")
                email = props.get("email") or props.get("contact", {}).get("email", "")

                buyer = {
                    "business_name": name,
                    "category": category,
                    "website": website,
                    "domain": normalize_domain(website),
                    "email": email.strip().lower() if email else "",
                    "email_source": "map_data" if email else "",
                    "phone": props.get("contact", {}).get("phone", props.get("phone", "")),
                    "address": props.get("address_line1", props.get("formatted", "")),
                    "city": props.get("city", ""),
                    "state": props.get("state", ""),
                    "lat": props.get("lat"),
                    "lon": props.get("lon"),
                    "source_api": "geoapify"
                }
                results.append(buyer)

            # Cache for 7 days
            if results:
                ApiCache.set_cache(cache_key, "geoapify", results, ttl_days=7)

            return results
        except Exception:
            return []
