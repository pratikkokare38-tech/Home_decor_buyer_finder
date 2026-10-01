from django.db import models
from django.contrib.auth.models import User
from apps.buyers.models import Buyer


class EmailTemplate(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body_html = models.TextField(help_text="Email body. Supports placeholders like {{buyer_name}}, {{seller_company}}, {{city}}")
    body_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.seller.username})"


class Campaign(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sending', 'Sending Pitch Emails'),
        ('done', 'Completed'),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, related_name='campaigns')
    buyers = models.ManyToManyField(Buyer, related_name='campaigns')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Campaign #{self.id} for {self.seller.username} ({self.status})"


class EmailLog(models.Model):
    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    )

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='email_logs')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='email_logs')
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    rendered_body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    provider_message_id = models.CharField(max_length=255, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Email to {self.recipient_email}: {self.status}"


class Unsubscribe(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    reason = models.CharField(max_length=255, blank=True, default='User requested opt-out')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Unsubscribed: {self.email}"
