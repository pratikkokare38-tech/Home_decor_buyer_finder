from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication pages & API
    path('', include('apps.accounts.urls')),

    # Buyer discovery pages & API
    path('', include('apps.buyers.urls')),

    # Email campaigns pages & API
    path('', include('apps.campaigns.urls')),
]
