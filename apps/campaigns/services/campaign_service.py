import time
from typing import Dict, List
from django.conf import settings
from apps.campaigns.models import Campaign, EmailLog, Unsubscribe
from apps.campaigns.services.template_renderer import TemplateRendererService
from integrations.email_sender import UnifiedEmailSender
from apps.accounts.models import SellerProfile
from apps.core.models import ApiUsage


class CampaignService:
    """
    Executes pitch email campaigns to target US buyers.
    Respects daily send quotas and opt-out unsubscribe lists.
    """
    def __init__(self):
        self.sender = UnifiedEmailSender()

    def execute_campaign(self, campaign: Campaign, request_host: str = "127.0.0.1:8000") -> Dict:
        campaign.status = 'sending'
        campaign.save()

        seller_profile, _ = SellerProfile.objects.get_or_create(user=campaign.seller)
        buyers = campaign.buyers.all()
        
        # 1. Get unsubscribed emails set
        unsubscribed_emails = set(Unsubscribe.objects.values_list('email', flat=True))

        # 2. Check Daily Limit
        daily_limit = getattr(settings, 'EMAIL_DAILY_LIMIT', 300)
        today_sent = ApiUsage.get_daily_credits("brevo") + ApiUsage.get_daily_credits("console_email")

        sent_count = 0
        failed_count = 0

        for buyer in buyers:
            if not buyer.email or buyer.email_status == 'invalid':
                continue

            if buyer.email.lower() in unsubscribed_emails:
                EmailLog.objects.create(
                    campaign=campaign,
                    buyer=buyer,
                    recipient_email=buyer.email,
                    subject="Skipped - Unsubscribed",
                    rendered_body="Skipped because recipient opted out via unsubscribe link.",
                    status='failed',
                    error_message='Recipient is on Unsubscribe list'
                )
                failed_count += 1
                continue

            if today_sent >= daily_limit:
                EmailLog.objects.create(
                    campaign=campaign,
                    buyer=buyer,
                    recipient_email=buyer.email,
                    subject="Queued - Daily Limit",
                    rendered_body="Queued for next day due to 300/day email quota limit.",
                    status='queued',
                    error_message='Daily email quota limit reached'
                )
                continue

            # Render template
            subject, html_body = TemplateRendererService.render(
                subject_template=campaign.template.subject,
                body_template=campaign.template.body_html,
                buyer=buyer,
                seller_profile=seller_profile,
                request_host=request_host
            )

            # Send Email
            result = self.sender.send_pitch_email(
                to_email=buyer.email,
                subject=subject,
                html_body=html_body,
                from_email=seller_profile.from_email,
                from_name=seller_profile.from_name
            )

            if result['status'] == 'sent':
                sent_count += 1
                today_sent += 1
                EmailLog.objects.create(
                    campaign=campaign,
                    buyer=buyer,
                    recipient_email=buyer.email,
                    subject=subject,
                    rendered_body=html_body,
                    status='sent',
                    provider_message_id=result.get('provider_message_id')
                )
            else:
                failed_count += 1
                EmailLog.objects.create(
                    campaign=campaign,
                    buyer=buyer,
                    recipient_email=buyer.email,
                    subject=subject,
                    rendered_body=html_body,
                    status='failed',
                    error_message=result.get('error')
                )

            # Polite throttle delay between sends
            time.sleep(0.1)

        campaign.status = 'done'
        campaign.sent_count = sent_count
        campaign.failed_count = failed_count
        campaign.save()

        return {
            'campaign_id': campaign.id,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_buyers': buyers.count()
        }
