import datetime
import logging
from typing import Dict, List
from django.utils import timezone

from integrations.base import BaseAPIClient
from apps.core.models import ApiCache, ApiUsage
from apps.core.utils import generate_cache_key, normalize_domain
from apps.core.constants import BUYER_CATEGORIES

logger = logging.getLogger(__name__)


class OverpassClient(BaseAPIClient):
    """
    OpenStreetMap Overpass API Client (Fallback Places Discovery).
    Free, no API key required. Respect polite query rates.
    """
    ENDPOINTS = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
    ]

    def __init__(self):
        super().__init__(base_url="https://overpass-api.de/api")

    def search_shops(self, category: str, lat: float, lon: float, radius_km: int = 50, limit: int = 30) -> List[Dict]:
        """
        Query OpenStreetMap nodes & ways for home decor stores near lat/lon.
        Uses optimized Overpass QL regex union queries for sub-second execution.
        """
        cache_key = generate_cache_key("overpass_shops", {
            "category": category, "lat": round(lat, 3), "lon": round(lon, 3), "radius": radius_km, "limit": limit
        })
        cached = ApiCache.objects.filter(cache_key=cache_key).first()
        if cached and cached.is_valid():
            return cached.response_data

        cat_info = BUYER_CATEGORIES.get(category, BUYER_CATEGORIES['all'])
        tags = cat_info.get('osm_tags', ['shop=furniture'])
        
        # Build ultra-fast regex filter for Overpass: shop~"^(furniture|interior_decoration|...)$"
        shop_values = "|".join([t.split("=")[-1] for t in tags if "=" in t])
        radius_meters = int(radius_km * 1000)
        query = f'[out:json][timeout:15];(node["shop"~"^({shop_values})$"](around:{radius_meters},{lat},{lon});way["shop"~"^({shop_values})$"](around:{radius_meters},{lat},{lon}););out center {limit};'

        data = None
        for ep in self.ENDPOINTS:
            try:
                response = self.request("POST", ep, data={"data": query}, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    ApiUsage.record_usage("overpass", credits=1)
                    break
            except Exception as err:
                logger.warning("Overpass endpoint %s failed: %s", ep, err)

        if not data or not isinstance(data, dict):
            return []

        results = []
        for element in (data.get("elements") or []):
            tags_dict = element.get("tags") or {}
            name = tags_dict.get("name")
            if not name:
                continue

            website = tags_dict.get("website") or tags_dict.get("contact:website", "")
            email = tags_dict.get("email") or tags_dict.get("contact:email", "")
            phone = tags_dict.get("phone") or tags_dict.get("contact:phone", "")
            
            street = tags_dict.get("addr:street", "")
            housenumber = tags_dict.get("addr:housenumber", "")
            address = f"{housenumber} {street}".strip() or tags_dict.get("addr:full", "")

            elem_lat = element.get("lat") or (element.get("center") or {}).get("lat", lat)
            elem_lon = element.get("lon") or (element.get("center") or {}).get("lon", lon)

            buyer = {
                "business_name": name,
                "category": category,
                "website": website,
                "domain": normalize_domain(website),
                "email": email.strip().lower() if email else "",
                "email_source": "map_data" if email else "",
                "phone": phone,
                "address": address,
                "city": tags_dict.get("addr:city", ""),
                "state": tags_dict.get("addr:state", ""),
                "lat": elem_lat,
                "lon": elem_lon,
                "source_api": "overpass"
            }
            results.append(buyer)

        # Cache for 7 days
        if results:
            ApiCache.set_cache(cache_key, "overpass", results, ttl_days=7)

        return results
