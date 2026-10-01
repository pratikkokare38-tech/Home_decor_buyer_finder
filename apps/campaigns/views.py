from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.campaigns.models import EmailTemplate, Campaign, EmailLog, Unsubscribe
from apps.campaigns.serializers import EmailTemplateSerializer, CampaignSerializer, EmailLogSerializer
from apps.campaigns.services.template_renderer import TemplateRendererService
from apps.campaigns.services.campaign_service import CampaignService
from apps.accounts.models import SellerProfile
from apps.buyers.models import Buyer


class TemplateListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates = EmailTemplate.objects.filter(seller=request.user)
        return Response(EmailTemplateSerializer(templates, many=True).data)

    def post(self, request):
        name = request.data.get('name', 'Pitch Template')
        subject = request.data.get('subject', 'Partnership Opportunity with {{seller_company}}')
        body_html = request.data.get('body_html', '<p>Hello {{buyer_name}},</p><p>We love your store in {{city}}.</p>')

        template = EmailTemplate.objects.create(
            seller=request.user,
            name=name,
            subject=subject,
            body_html=body_html
        )
        return Response(EmailTemplateSerializer(template).data, status=status.HTTP_201_CREATED)


class TemplateDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            template = EmailTemplate.objects.get(pk=pk, seller=request.user)
            template.name = request.data.get('name', template.name)
            template.subject = request.data.get('subject', template.subject)
            template.body_html = request.data.get('body_html', template.body_html)
            template.save()
            return Response(EmailTemplateSerializer(template).data)
        except EmailTemplate.DoesNotExist:
            return Response({'error': {'code': 'NOT_FOUND', 'message': 'Template not found'}}, status=status.HTTP_404_NOT_FOUND)


class PreviewTemplateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subject_template = request.data.get('subject', 'Partnership with {{seller_company}}')
        body_template = request.data.get('body_html', '<p>Hello {{buyer_name}}</p>')
        buyer_id = request.data.get('buyer_id')

        buyer = Buyer.objects.filter(id=buyer_id, seller=request.user).first() if buyer_id else Buyer.objects.filter(seller=request.user).first()
        if not buyer:
            buyer = Buyer(business_name="Austin Home Decor Boutique", city="Austin", website="https://austindecor.com", email="info@austindecor.com")

        profile, _ = SellerProfile.objects.get_or_create(user=request.user)
        host = request.get_host()

        rendered_subject, rendered_body = TemplateRendererService.render(
            subject_template, body_template, buyer, profile, host
        )

        return Response({
            'rendered_subject': rendered_subject,
            'rendered_body': rendered_body
        })


class CampaignCreateSendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        template_id = request.data.get('template_id')
        buyer_ids = request.data.get('buyer_ids', [])

        if not buyer_ids:
            return Response({'error': {'code': 'BAD_REQUEST', 'message': 'No buyers selected for campaign'}}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create template
        if template_id:
            template = EmailTemplate.objects.get(pk=template_id, seller=request.user)
        else:
            template = EmailTemplate.objects.create(
                seller=request.user,
                name=request.data.get('template_name', 'Direct Pitch'),
                subject=request.data.get('subject', 'Wholesale Home Decor Collection for {{buyer_name}}'),
                body_html=request.data.get('body_html', '<p>Hello {{buyer_name}},</p><p>We would love to introduce our products to your store in {{city}}.</p>')
            )

        campaign = Campaign.objects.create(
            seller=request.user,
            template=template,
            total_recipients=len(buyer_ids),
            status='draft'
        )
        buyers = Buyer.objects.filter(id__in=buyer_ids, seller=request.user)
        campaign.buyers.set(buyers)

        # Execute campaign immediately
        service = CampaignService()
        result = service.execute_campaign(campaign, request.get_host())

        return Response(CampaignSerializer(campaign).data, status=status.HTTP_201_CREATED)


class CampaignLogsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            campaign = Campaign.objects.get(pk=pk, seller=request.user)
            logs = campaign.email_logs.all()
            return Response(EmailLogSerializer(logs, many=True).data)
        except Campaign.DoesNotExist:
            return Response({'error': {'code': 'NOT_FOUND', 'message': 'Campaign not found'}}, status=status.HTTP_404_NOT_FOUND)
