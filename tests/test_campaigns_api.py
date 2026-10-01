import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.accounts.models import SellerProfile
from apps.buyers.models import SearchQuery, Buyer
from apps.campaigns.models import Campaign, EmailLog, Unsubscribe
from apps.campaigns.services.template_renderer import TemplateRendererService


@pytest.mark.django_db
def test_template_rendering_and_can_spam_footer():
    user = User.objects.create_user(username='test_seller', password='Password123')
    profile, _ = SellerProfile.objects.get_or_create(user=user)
    profile.company_name = "Austin Crafts LLC"
    profile.from_name = "Jane Seller"
    profile.postal_address = "500 Austin Blvd, Austin, TX 78701"
    profile.save()

    query = SearchQuery.objects.create(seller=user, category="furniture", state="TX", city="Austin")
    buyer = Buyer.objects.create(
        seller=user,
        search_query=query,
        business_name="Austin Modern Living",
        city="Austin",
        email="buyer@austinmodernliving.com",
        email_status="valid"
    )

    subject_tpl = "Partnership with {{seller_company}}"
    body_tpl = "<p>Hello {{buyer_name}}, we love your store in {{city}}.</p>"

    subj, body = TemplateRendererService.render(subject_tpl, body_tpl, buyer, profile, "localhost:8000")

    assert "Austin Crafts LLC" in subj
    assert "Austin Modern Living" in body
    assert "500 Austin Blvd, Austin, TX 78701" in body
    assert "http://localhost:8000/unsubscribe/?email=buyer@austinmodernliving.com" in body


@pytest.mark.django_db
def test_campaign_execution_and_unsubscribe_skip(client):
    user = User.objects.create_user(username='campaign_seller', password='Password123')
    client.login(username='campaign_seller', password='Password123')

    query = SearchQuery.objects.create(seller=user, category="furniture", state="TX", city="Austin")
    buyer1 = Buyer.objects.create(
        seller=user, search_query=query, business_name="Store 1", email="valid@buyer1.com", email_status="valid"
    )
    buyer2 = Buyer.objects.create(
        seller=user, search_query=query, business_name="Store 2", email="optout@buyer2.com", email_status="valid"
    )

    # Opt out buyer 2
    Unsubscribe.objects.create(email="optout@buyer2.com")

    campaign_url = reverse('api_campaign_create_send')
    response = client.post(
        campaign_url,
        data={
            "subject": "Hello {{buyer_name}}",
            "body_html": "<p>Pitch for {{seller_company}}</p>",
            "buyer_ids": [buyer1.id, buyer2.id]
        },
        content_type="application/json"
    )

    assert response.status_code == 201
    campaign_id = response.data['id']

    campaign = Campaign.objects.get(pk=campaign_id)
    assert campaign.status == 'done'
    assert campaign.sent_count == 1
    assert campaign.failed_count == 1

    logs = EmailLog.objects.filter(campaign=campaign)
    assert logs.filter(recipient_email="valid@buyer1.com", status="sent").exists()
    assert logs.filter(recipient_email="optout@buyer2.com", status="failed").exists()
