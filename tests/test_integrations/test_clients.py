import pytest
import responses
from integrations.geoapify import GeoapifyClient
from integrations.overpass import OverpassClient
from integrations.website_crawler import WebsiteCrawlerClient
from integrations.hunter import HunterClient
from apps.core.models import ApiUsage


@pytest.mark.django_db
@responses.activate
def test_geoapify_geocode_and_places():
    # Mock Geoapify geocode
    responses.add(
        responses.GET,
        "https://api.geoapify.com/v1/geocode/search",
        json={"features": [{"properties": {"lat": 30.2672, "lon": -97.7431, "city": "Austin", "state": "Texas"}}]},
        status=200
    )
    
    # Mock Geoapify places
    responses.add(
        responses.GET,
        "https://api.geoapify.com/v2/places",
        json={"features": [{
            "properties": {
                "name": "Austin Modern Living",
                "website": "https://austinmodernliving.com",
                "phone": "+1 512-555-0199",
                "formatted": "101 S Congress Ave, Austin, TX"
            }
        }]},
        status=200
    )

    client = GeoapifyClient()
    client.api_key = "test_key"
    
    geocode = client.geocode("Austin", "TX")
    assert geocode['lat'] == 30.2672

    places = client.search_places("furniture", 30.2672, -97.7431, radius_km=10, limit=5)
    assert len(places) == 1
    assert places[0]['business_name'] == "Austin Modern Living"
    assert places[0]['domain'] == "austinmodernliving.com"


@pytest.mark.django_db
@responses.activate
def test_overpass_search_shops():
    responses.add(
        responses.POST,
        "https://overpass-api.de/api/interpreter",
        json={"elements": [{
            "tags": {
                "name": "Texas Artisan Furniture",
                "website": "http://texasartisan.com",
                "phone": "+1 512-555-0144"
            },
            "lat": 30.2672,
            "lon": -97.7431
        }]},
        status=200
    )

    client = OverpassClient()
    results = client.search_shops("furniture", 30.2672, -97.7431, radius_km=15, limit=5)
    assert len(results) == 1
    assert results[0]['business_name'] == "Texas Artisan Furniture"
    assert results[0]['domain'] == "texasartisan.com"


@pytest.mark.django_db
@responses.activate
def test_website_crawler_extracts_contact_email():
    html_content = """
    <html>
        <body>
            <h1>Austin Decor Studio</h1>
            <p>Contact our purchasing manager at sales@austindecorstudio.com or info@austindecorstudio.com</p>
        </body>
    </html>
    """
    responses.add(
        responses.GET,
        "http://austindecorstudio.com",
        body=html_content,
        status=200
    )

    crawler = WebsiteCrawlerClient()
    emails = crawler.find_emails("http://austindecorstudio.com")
    assert len(emails) >= 1
    assert "sales@austindecorstudio.com" in emails or "info@austindecorstudio.com" in emails


@pytest.mark.django_db
@responses.activate
def test_hunter_domain_search():
    responses.add(
        responses.GET,
        "https://api.hunter.io/v2/domain-search",
        json={"data": {"emails": [{"value": "orders@decorbuyer.com", "confidence": 95}]}},
        status=200
    )

    hunter = HunterClient()
    hunter.api_key = "test_hunter_key"
    
    emails = hunter.domain_search("decorbuyer.com", limit=2)
    assert len(emails) == 1
    assert emails[0]['email'] == "orders@decorbuyer.com"
    assert ApiUsage.get_monthly_credits("hunter") == 1
