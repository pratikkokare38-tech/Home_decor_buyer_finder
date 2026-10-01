import concurrent.futures
from typing import List
from django.conf import settings
from apps.buyers.models import SearchQuery, Buyer
from integrations.geoapify import GeoapifyClient
from integrations.overpass import OverpassClient
from apps.buyers.services.deduplication import DeduplicationService
from apps.buyers.services.email_finder_service import EmailFinderService


class DiscoveryPipelineService:
    """
    Orchestrates the full US Buyer Discovery Pipeline:
    1. Geocode US City/State -> Lat/Lon
    2. Primary Places Search (Geoapify) + Fallback (OpenStreetMap Overpass)
    3. Deduplicate businesses
    4. Layered Email Discovery & Local MX Verification
    5. Save Buyer records in DB
    """
    def __init__(self):
        self.geoapify = GeoapifyClient()
        self.overpass = OverpassClient()
        self.email_finder = EmailFinderService()

    def run_search(self, search_query: SearchQuery) -> int:
        search_query.status = 'running'
        search_query.save()

        try:
            # Step 1: Geocode
            coords = self.geoapify.geocode(search_query.city, search_query.state, "US")
            if not coords or 'lat' not in coords:
                search_query.status = 'failed'
                search_query.error_message = f"Could not geocode US city: {search_query.city}, {search_query.state}"
                search_query.save()
                return 0

            lat, lon = coords['lat'], coords['lon']
            max_limit = getattr(settings, 'MAX_BUYERS_PER_SEARCH', 30)

            # Step 2: Places Discovery
            buyers_data = self.geoapify.search_places(
                category=search_query.category,
                lat=lat,
                lon=lon,
                radius_km=search_query.radius_km,
                limit=max_limit
            )

            # Fallback to Overpass if Geoapify yields fewer than 10 results
            if len(buyers_data) < 10:
                osm_data = self.overpass.search_shops(
                    category=search_query.category,
                    lat=lat,
                    lon=lon,
                    radius_km=search_query.radius_km,
                    limit=max_limit
                )
                buyers_data.extend(osm_data)

            # Step 3: Deduplicate
            unique_buyers = DeduplicationService.deduplicate(buyers_data)[:max_limit]

            # Step 4: Layered Email Finding (Multithreaded thread pool, max 5 workers)
            processed_buyers = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.email_finder.discover_email, b) for b in unique_buyers]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        processed_buyers.append(future.result())
                    except Exception:
                        pass

            # Step 5: Save Buyer models to DB
            saved_count = 0
            for b_data in processed_buyers:
                # Prevent seller level duplicate email spam
                email = b_data.get('email')
                if email and Buyer.objects.filter(seller=search_query.seller, email=email).exists():
                    continue

                Buyer.objects.create(
                    seller=search_query.seller,
                    search_query=search_query,
                    business_name=b_data.get('business_name', 'Unknown Business'),
                    category=search_query.category,
                    website=b_data.get('website'),
                    domain=b_data.get('domain', ''),
                    email=b_data.get('email'),
                    email_source=b_data.get('email_source', 'none'),
                    email_status=b_data.get('email_status', 'unverified'),
                    phone=b_data.get('phone'),
                    address=b_data.get('address'),
                    city=b_data.get('city') or search_query.city,
                    state=b_data.get('state') or search_query.state,
                    lat=b_data.get('lat'),
                    lon=b_data.get('lon'),
                    source_api=b_data.get('source_api', 'geoapify')
                )
                saved_count += 1

            search_query.status = 'done'
            search_query.total_found = saved_count
            search_query.save()
            return saved_count

        except Exception as err:
            search_query.status = 'failed'
            search_query.error_message = str(err)
            search_query.save()
            return 0
