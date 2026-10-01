from typing import Dict, Optional
from django.conf import settings
from django.core.mail import send_mail
from integrations.base import BaseAPIClient
from apps.core.models import ApiUsage


class UnifiedEmailSender(BaseAPIClient):
    """
    Unified transactional Email API client supporting Brevo, Resend, or Django Console backend.
    Enforces dev mode protection: never sends real external emails when DEBUG is True or EMAIL_PROVIDER='console'.
    """
    def __init__(self):
        self.provider = getattr(settings, 'EMAIL_PROVIDER', 'console').lower()
        self.brevo_key = getattr(settings, 'BREVO_API_KEY', '')
        self.resend_key = getattr(settings, 'RESEND_API_KEY', '')
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@homedecorbuyerfinder.com')
        self.from_name = getattr(settings, 'DEFAULT_FROM_NAME', 'Home Decor Buyer Finder')
        super().__init__()

    def send_pitch_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str = "",
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> Dict:
        """
        Send single pitch email via Brevo / Resend / Console.
        Returns dict with status ('sent' | 'failed'), provider_message_id, and error message.
        """
        sender_email = from_email or self.from_email
        sender_name = from_name or self.from_name

        # Enforce local console/mock email backend during development/testing
        if settings.DEBUG or self.provider == 'console' or not (self.brevo_key or self.resend_key):
            try:
                send_mail(
                    subject=subject,
                    message=text_body or html_body,
                    html_message=html_body,
                    from_email=f"{sender_name} <{sender_email}>",
                    recipient_list=[to_email],
                    fail_silently=False
                )
                ApiUsage.record_usage("console_email", credits=1)
                return {'status': 'sent', 'provider_message_id': 'console-dev-id', 'error': None}
            except Exception as err:
                return {'status': 'failed', 'provider_message_id': None, 'error': str(err)}

        # Brevo (formerly Sendinblue) Transactional API (300 emails/day free)
        if self.provider == 'brevo' and self.brevo_key:
            return self._send_via_brevo(to_email, subject, html_body, text_body, sender_email, sender_name)

        # Resend Transactional API (3,000 emails/month free)
        if self.provider == 'resend' and self.resend_key:
            return self._send_via_resend(to_email, subject, html_body, text_body, sender_email, sender_name)

        # Fallback to console
        send_mail(
            subject=subject,
            message=text_body or html_body,
            html_message=html_body,
            from_email=f"{sender_name} <{sender_email}>",
            recipient_list=[to_email],
            fail_silently=True
        )
        return {'status': 'sent', 'provider_message_id': 'fallback-dev-id', 'error': None}

    def _send_via_brevo(self, to_email: str, subject: str, html_body: str, text_body: str, from_email: str, from_name: str) -> Dict:
        headers = {
            "accept": "application/json",
            "api-key": self.brevo_key,
            "content-type": "application/json"
        }
        payload = {
            "sender": {"name": from_name, "email": from_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_body,
            "textContent": text_body or html_body
        }
        try:
            resp = self.session.post("https://api.brevo.com/v3/smtp/email", headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            ApiUsage.record_usage("brevo", credits=1)
            return {'status': 'sent', 'provider_message_id': data.get('messageId', 'brevo-ok'), 'error': None}
        except Exception as err:
            return {'status': 'failed', 'provider_message_id': None, 'error': str(err)}

    def _send_via_resend(self, to_email: str, subject: str, html_body: str, text_body: str, from_email: str, from_name: str) -> Dict:
        headers = {
            "Authorization": f"Bearer {self.resend_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": f"{from_name} <{from_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_body,
            "text": text_body or html_body
        }
        try:
            resp = self.session.post("https://api.resend.com/emails", headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            ApiUsage.record_usage("resend", credits=1)
            return {'status': 'sent', 'provider_message_id': data.get('id', 'resend-ok'), 'error': None}
        except Exception as err:
            return {'status': 'failed', 'provider_message_id': None, 'error': str(err)}
