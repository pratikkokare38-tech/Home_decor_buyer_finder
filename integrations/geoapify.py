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
    Falls back gracefully to OpenStreetMap Nominatim if no API key is provided.
    """
    def __init__(self):
        super().__init__(base_url="https://api.geoapify.com")
        self.api_key = settings.GEOAPIFY_API_KEY

    def geocode(self, city: str, state: str, country: str = "US") -> Optional[Dict]:
        """
        Geocode a US city/state into latitude and longitude coordinates.
        """
        cache_key = generate_cache_key("geo_geocode", {"city": city.lower().strip(), "state": state.upper().strip(), "country": country})
        cached = ApiCache.objects.filter(cache_key=cache_key).first()
        if cached and cached.is_valid():
            return cached.response_data

        if not self.api_key:
            # Free Nominatim geocoding fallback for US cities
            try:
                nom_resp = self.session.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": f"{city}, {state}, USA", "format": "json", "limit": 1},
                    timeout=10
                )
                if nom_resp.status_code == 200 and nom_resp.json():
                    first = nom_resp.json()[0]
                    res = {
                        "lat": float(first["lat"]),
                        "lon": float(first["lon"]),
                        "city": city,
                        "state": state,
                        "formatted": first.get("display_name", f"{city}, {state}")
                    }
                    expires_at = timezone.now() + datetime.timedelta(days=30)
                    ApiCache.objects.create(
                        cache_key=cache_key,
                        provider="nominatim",
                        response_data=res,
                        expires_at=expires_at
                    )
                    return res
            except Exception:
                pass

            return {"lat": 30.2672, "lon": -97.7431, "city": city, "state": state}

        params = {
            "city": city,
            "state": state,
            "country": country,
            "apiKey": self.api_key
        }

        try:
            response = self.request("GET", "/v1/geocode/search", params=params)
            data = response.json()
            ApiUsage.record_usage("geoapify", credits=1)

            features = data.get("features", [])
            if not features:
                return None

            props = features[0]["properties"]
            result = {
                "lat": props.get("lat"),
                "lon": props.get("lon"),
                "city": props.get("city", city),
                "state": props.get("state", state),
                "formatted": props.get("formatted", f"{city}, {state}")
            }

            # Cache for 30 days
            expires_at = timezone.now() + datetime.timedelta(days=30)
            ApiCache.objects.create(
                cache_key=cache_key,
                provider="geoapify",
                response_data=result,
                expires_at=expires_at
            )

            return result
        except Exception:
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
        radius_meters = radius_km * 1000

        params = {
            "categories": geo_cat_str,
            "filter": f"circle:{lon},{lat},{radius_meters}",
            "limit": limit,
            "apiKey": self.api_key
        }

        try:
            response = self.request("GET", "/v2/places", params=params)
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
                expires_at = timezone.now() + datetime.timedelta(days=7)
                ApiCache.objects.create(
                    cache_key=cache_key,
                    provider="geoapify",
                    response_data=results,
                    expires_at=expires_at
                )

            return results
        except Exception:
            return []
