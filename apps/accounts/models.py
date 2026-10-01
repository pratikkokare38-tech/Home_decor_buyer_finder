from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class SellerProfile(models.Model):
    """
    Profile for US Home Decor Sellers.
    Stores company information, contact email, and physical postal address required for email compliance.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    company_name = models.CharField(max_length=255, help_text="Your Business or Brand Name")
    website = models.URLField(max_length=500, blank=True, null=True, help_text="Company Website URL")
    product_categories = models.CharField(
        max_length=500,
        blank=True,
        help_text="Primary product categories (e.g., Furniture, Lighting, Wall Art, Rugs)"
    )
    from_name = models.CharField(max_length=150, help_text="Sender name displayed in buyer pitch emails")
    from_email = models.EmailField(help_text="Verified email address used for sending pitches")
    postal_address = models.TextField(
        help_text="Physical postal address included in email footer for CAN-SPAM compliance"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.user.username})"


@receiver(post_save, sender=User)
def create_or_update_seller_profile(sender, instance, created, **kwargs):
    """Ensure a SellerProfile instance exists for every User."""
    if created:
        SellerProfile.objects.create(
            user=instance,
            company_name=instance.username,
            from_name=instance.get_full_name() or instance.username,
            from_email=instance.email or f"{instance.username}@example.com",
            postal_address="123 Main St, Austin, TX 78701"
        )
