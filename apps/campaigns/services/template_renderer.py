from typing import Tuple
from django.conf import settings
from apps.buyers.models import Buyer
from apps.accounts.models import SellerProfile


class TemplateRendererService:
    """
    Renders email subject and HTML body with dynamic placeholders
    and appends CAN-SPAM compliant footer (Seller Address + Unsubscribe Link).
    """
    @classmethod
    def render(cls, subject_template: str, body_template: str, buyer: Buyer, seller_profile: SellerProfile, request_host: str = "127.0.0.1:8000") -> Tuple[str, str]:
        buyer_name = buyer.business_name or "Home Decor Buyer"
        seller_company = seller_profile.company_name or "Our US Artisan Decor Brand"
        seller_name = seller_profile.from_name or "Sales Team"
        city = buyer.city or "your area"

        replacements = {
            '{{buyer_name}}': buyer_name,
            '{{seller_company}}': seller_company,
            '{{seller_name}}': seller_name,
            '{{city}}': city,
            '{{website}}': buyer.website or '',
        }

        rendered_subject = subject_template
        rendered_body = body_template

        for token, val in replacements.items():
            rendered_subject = rendered_subject.replace(token, val)
            rendered_body = rendered_body.replace(token, val)

        # Generate unsubscribe link
        unsub_link = f"http://{request_host}/unsubscribe/?email={buyer.email}"
        postal_address = seller_profile.postal_address or settings.SENDER_POSTAL_ADDRESS

        # Append CAN-SPAM Compliance Footer
        footer_html = f"""
        <br><hr style="border:0; border-top:1px solid #e2e8f0; margin: 25px 0;">
        <footer style="font-size: 12px; color: #718096; line-height: 1.5;">
            <p><strong>{seller_company}</strong> • {postal_address}</p>
            <p>You received this commercial message because your business buys home decor items in {city}.</p>
            <p><a href="{unsub_link}" style="color: #4c51bf; text-decoration: underline;">Unsubscribe / Opt-Out from future pitches</a></p>
        </footer>
        """

        full_html = rendered_body + footer_html
        return rendered_subject, full_html
