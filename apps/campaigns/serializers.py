from rest_framework import serializers
from apps.campaigns.models import EmailTemplate, Campaign, EmailLog, Unsubscribe
from apps.buyers.serializers import BuyerSerializer


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'subject', 'body_html', 'body_text', 'created_at']


class EmailLogSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.business_name', read_only=True)

    class Meta:
        model = EmailLog
        fields = ['id', 'buyer_name', 'recipient_email', 'subject', 'status', 'provider_message_id', 'error_message', 'sent_at']


class CampaignSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = Campaign
        fields = ['id', 'template', 'template_name', 'status', 'total_recipients', 'sent_count', 'failed_count', 'created_at']
