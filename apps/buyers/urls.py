from django.urls import path
from . import page_views, views

urlpatterns = [
    # Page Routes
    path('', page_views.search_page_view, name='search_page'),
    path('search/', page_views.search_page_view, name='search_page'),
    path('results/<int:search_id>/', page_views.results_page_view, name='results_page'),

    # REST API Routes
    path('api/buyers/search/', views.StartSearchAPIView.as_view(), name='api_buyers_search'),
    path('api/buyers/searches/', views.SearchQueryListAPIView.as_view(), name='api_buyers_searches'),
    path('api/buyers/searches/<int:pk>/', views.SearchQueryDetailAPIView.as_view(), name='api_buyers_search_detail'),
    path('api/buyers/', views.BuyerListAPIView.as_view(), name='api_buyers_list'),
    path('api/usage/', views.QuotaUsageAPIView.as_view(), name='api_usage'),
]
