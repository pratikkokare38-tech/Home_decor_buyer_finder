import concurrent.futures
import logging
from typing import List, Dict
from django.conf import settings
from apps.buyers.models import SearchQuery, Buyer
from integrations.geoapify import GeoapifyClient
from integrations.overpass import OverpassClient
from apps.buyers.services.deduplication import DeduplicationService
from apps.buyers.services.email_finder_service import EmailFinderService

logger = logging.getLogger(__name__)


class DiscoveryPipelineService:
    """
    Orchestrates the full US Buyer Discovery Pipeline:
    1. Geocode US City/State -> Lat/Lon (Geoapify + Nominatim + State fallback)
    2. Primary Places Search (Geoapify) + Fallback (OpenStreetMap Overpass)
    3. Deduplicate businesses
    4. Layered Email Discovery & Local MX Verification (Concurrent & bounded)
    5. Save Buyer records in DB
    """
    def __init__(self):
        self.geoapify = GeoapifyClient()
        self.overpass = OverpassClient()
        self.email_finder = EmailFinderService()

    def _process_buyer_email(self, buyer_dict: Dict) -> Dict:
        """Helper to process email discovery safely for a single buyer."""
        try:
            return self.email_finder.discover_email(buyer_dict)
        except Exception as err:
            logger.warning("Email discovery error for %s: %s", buyer_dict.get('business_name'), err)
            return buyer_dict

    def run_search(self, search_query: SearchQuery) -> int:
        search_query.status = 'running'
        search_query.save()

        try:
            # Step 1: Geocode
            coords = self.geoapify.geocode(search_query.city, search_query.state, "US")
            if not coords or 'lat' not in coords:
                search_query.status = 'failed'
                search_query.error_message = f"Could not geocode US location: {search_query.city}, {search_query.state}"
                search_query.save()
                return 0

            lat, lon = coords['lat'], coords['lon']
            max_limit = getattr(settings, 'MAX_BUYERS_PER_SEARCH', 30)

            # Step 2: Places Discovery (Geoapify first, Overpass fallback)
            buyers_data = []
            try:
                buyers_data = self.geoapify.search_places(
                    category=search_query.category,
                    lat=lat,
                    lon=lon,
                    radius_km=search_query.radius_km,
                    limit=max_limit
                )
            except Exception as err:
                logger.warning("Geoapify places search failed: %s", err)

            # Fallback to Overpass if Geoapify yields fewer than 10 results
            if len(buyers_data) < 10:
                try:
                    osm_data = self.overpass.search_shops(
                        category=search_query.category,
                        lat=lat,
                        lon=lon,
                        radius_km=search_query.radius_km,
                        limit=max_limit
                    )
                    buyers_data.extend(osm_data)
                except Exception as err:
                    logger.warning("Overpass fallback places search failed: %s", err)

            # Step 3: Deduplicate
            unique_buyers = DeduplicationService.deduplicate(buyers_data)[:max_limit]

            # Step 4: Layered Email Finding (Fast concurrent processing with max 6 workers)
            processed_buyers = []
            if unique_buyers:
                with concurrent.futures.ThreadPoolExecutor(max_workers=min(6, len(unique_buyers))) as executor:
                    processed_buyers = list(executor.map(self._process_buyer_email, unique_buyers))

            # Step 5: Save Buyer models to DB
            saved_count = 0
            for b_data in processed_buyers:
                if not isinstance(b_data, dict):
                    continue
                # Prevent seller level duplicate email spam
                email = b_data.get('email')
                if email and Buyer.objects.filter(seller=search_query.seller, email=email).exists():
                    continue

                try:
                    Buyer.objects.create(
                        seller=search_query.seller,
                        search_query=search_query,
                        business_name=str(b_data.get('business_name') or 'Unknown Business')[:250],
                        category=str(search_query.category)[:95],
                        website=str(b_data.get('website'))[:490] if b_data.get('website') else None,
                        domain=str(b_data.get('domain') or '')[:250],
                        email=str(b_data.get('email'))[:250] if b_data.get('email') else None,
                        email_source=str(b_data.get('email_source') or 'none')[:30],
                        email_status=str(b_data.get('email_status') or 'unverified')[:20],
                        phone=str(b_data.get('phone'))[:45] if b_data.get('phone') else None,
                        address=b_data.get('address'),
                        city=str(b_data.get('city') or search_query.city)[:140],
                        state=str(b_data.get('state') or search_query.state)[:45],
                        lat=b_data.get('lat'),
                        lon=b_data.get('lon'),
                        source_api=str(b_data.get('source_api') or 'geoapify')[:45]
                    )
                    saved_count += 1
                except Exception as save_err:
                    logger.warning("Could not save buyer %s: %s", b_data.get('business_name'), save_err)

            search_query.status = 'done'
            search_query.total_found = saved_count
            search_query.save()
            return saved_count

        except Exception as err:
            logger.exception("Discovery pipeline error: %s", err)
            search_query.status = 'failed'
            search_query.error_message = str(err)
            search_query.save()
            return 0
