from django.db import models
from django.contrib.auth.models import User


class SearchQuery(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running Discovery Pipeline'),
        ('done', 'Completed'),
        ('failed', 'Failed'),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_queries')
    category = models.CharField(max_length=100)
    state = models.CharField(max_length=10)
    city = models.CharField(max_length=150)
    radius_km = models.IntegerField(default=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_found = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category} in {self.city}, {self.state} ({self.status})"


class Buyer(models.Model):
    EMAIL_SOURCE_CHOICES = (
        ('map_data', 'Map Data (Geoapify/OSM)'),
        ('crawler', 'Website Contact Crawler'),
        ('hunter', 'Hunter.io API'),
        ('none', 'No Email Found'),
    )

    EMAIL_STATUS_CHOICES = (
        ('unverified', 'Unverified'),
        ('valid', 'Valid / Verified'),
        ('risky', 'Risky / Catch-All'),
        ('invalid', 'Invalid / No MX'),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyers')
    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name='buyers')
    business_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    website = models.URLField(max_length=500, blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, db_index=True)
    email = models.EmailField(blank=True, null=True, db_index=True)
    email_source = models.CharField(max_length=30, choices=EMAIL_SOURCE_CHOICES, default='none')
    email_status = models.CharField(max_length=20, choices=EMAIL_STATUS_CHOICES, default='unverified')
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=150, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    source_api = models.CharField(max_length=50, default='geoapify')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business_name} ({self.email or 'No email'})"
