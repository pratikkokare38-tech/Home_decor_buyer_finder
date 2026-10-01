import pytest
import responses
from django.urls import reverse
from django.contrib.auth.models import User
from apps.buyers.models import SearchQuery, Buyer


@pytest.mark.django_db
@responses.activate
def test_buyer_search_and_pipeline(client, settings):
    settings.GEOAPIFY_API_KEY = "test_geoapify_key"

    user = User.objects.create_user(username='texasseller', password='Password123')
    client.login(username='texasseller', password='Password123')

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
                "name": "Austin Decor Showcase",
                "website": "https://austindecorshowcase.com",
                "phone": "+1 512-555-0188",
                "formatted": "200 E 6th St, Austin, TX",
                "email": "purchasing@austindecorshowcase.com"
            }
        }]},
        status=200
    )

    search_api_url = reverse('api_buyers_search')
    response = client.post(
        search_api_url,
        data={"category": "furniture", "state": "TX", "city": "Austin", "radius_km": 50},
        content_type="application/json"
    )

    assert response.status_code == 201
    search_id = response.data['id']

    query = SearchQuery.objects.get(pk=search_id)
    assert query.status == 'done'
    assert query.total_found == 1

    buyer = Buyer.objects.get(search_query=query)
    assert buyer.business_name == "Austin Decor Showcase"
    assert buyer.email == "purchasing@austindecorshowcase.com"
    assert buyer.email_status == "valid"
