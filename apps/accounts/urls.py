from django.urls import path
from . import views

urlpatterns = [
    # Template Page Routes
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile_page'),

    # DRF API Routes
    path('api/auth/register/', views.RegisterAPIView.as_view(), name='api_auth_register'),
    path('api/auth/login/', views.LoginAPIView.as_view(), name='api_auth_login'),
    path('api/auth/logout/', views.LogoutAPIView.as_view(), name='api_auth_logout'),
    path('api/auth/me/', views.CurrentUserAPIView.as_view(), name='api_auth_me'),
]
