import datetime
from django.db import models
from django.utils import timezone


class ApiCache(models.Model):
    """
    Stores API responses keyed by hash to prevent redundant external API calls.
    TTL defaults: 7 days for places search, 30 days for email discovery.
    """
    cache_key = models.CharField(max_length=255, unique=True, db_index=True)
    provider = models.CharField(max_length=50)
    response_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        verbose_name = 'API Cache'
        verbose_name_plural = 'API Caches'

    def is_valid(self):
        return timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.provider}:{self.cache_key} (valid until {self.expires_at})"


class ApiUsage(models.Model):
    """
    Tracks external API call counts and credit usage per provider per day.
    """
    provider = models.CharField(max_length=50, db_index=True)
    date = models.DateField(default=timezone.now, db_index=True)
    calls_count = models.IntegerField(default=0)
    credits_used = models.IntegerField(default=0)

    class Meta:
        unique_together = ('provider', 'date')
        verbose_name = 'API Usage'
        verbose_name_plural = 'API Usages'

    @classmethod
    def record_usage(cls, provider: str, credits: int = 1):
        today = timezone.now().date()
        usage, _ = cls.objects.get_or_create(provider=provider, date=today)
        usage.calls_count += 1
        usage.credits_used += credits
        usage.save()
        return usage

    @classmethod
    def get_monthly_credits(cls, provider: str) -> int:
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        usages = cls.objects.filter(provider=provider, date__gte=start_of_month)
        return sum(u.credits_used for u in usages)

    @classmethod
    def get_daily_credits(cls, provider: str) -> int:
        today = timezone.now().date()
        usage = cls.objects.filter(provider=provider, date=today).first()
        return usage.credits_used if usage else 0

    def __str__(self):
        return f"{self.provider} on {self.date}: {self.credits_used} credits"
