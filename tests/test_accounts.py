import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.accounts.models import SellerProfile


@pytest.mark.django_db
def test_seller_registration_flow(client):
    register_url = reverse('register')
    payload = {
        'username': 'texashomedecor',
        'email': 'seller@texashomedecor.com',
        'password': 'SecurePassword123',
        'confirm_password': 'SecurePassword123',
        'company_name': 'Texas Home Decor LLC',
        'from_name': 'Austin Seller',
        'postal_address': '100 Congress Ave, Austin, TX 78701'
    }
    response = client.post(register_url, payload)
    assert response.status_code == 302  # Redirects to search page on success

    user = User.objects.get(username='texashomedecor')
    assert user.email == 'seller@texashomedecor.com'
    assert user.seller_profile.company_name == 'Texas Home Decor LLC'
    assert user.seller_profile.postal_address == '100 Congress Ave, Austin, TX 78701'


@pytest.mark.django_db
def test_seller_login_and_logout(client):
    user = User.objects.create_user(username='austinartisan', email='artisan@austin.com', password='Password123')
    
    # Test Login
    login_url = reverse('login')
    response = client.post(login_url, {'username': 'austinartisan', 'password': 'Password123'})
    assert response.status_code == 302

    # Test Logout
    logout_url = reverse('logout')
    response = client.post(logout_url)
    assert response.status_code == 302
