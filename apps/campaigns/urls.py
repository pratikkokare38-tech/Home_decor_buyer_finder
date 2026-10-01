from django.urls import path
from . import page_views, views

urlpatterns = [
    # Page Routes
    path('campaigns/compose/', page_views.compose_page_view, name='campaign_compose'),
    path('campaigns/<int:campaign_id>/confirm/', page_views.confirm_page_view, name='campaign_confirm'),
    path('campaigns/history/', page_views.history_page_view, name='campaign_history'),
    path('unsubscribe/', page_views.unsubscribe_page_view, name='unsubscribe_page'),

    # REST API Routes
    path('api/templates/', views.TemplateListCreateAPIView.as_view(), name='api_templates'),
    path('api/templates/<int:pk>/', views.TemplateDetailAPIView.as_view(), name='api_template_detail'),
    path('api/templates/preview/', views.PreviewTemplateAPIView.as_view(), name='api_template_preview'),
    path('api/campaigns/', views.CampaignCreateSendAPIView.as_view(), name='api_campaign_create_send'),
    path('api/campaigns/<int:pk>/logs/', views.CampaignLogsAPIView.as_view(), name='api_campaign_logs'),
]
