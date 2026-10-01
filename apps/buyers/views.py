from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.buyers.models import SearchQuery, Buyer
from apps.buyers.serializers import SearchQuerySerializer, BuyerSerializer
from apps.buyers.services.discovery_service import DiscoveryPipelineService
from apps.core.models import ApiUsage
from django.conf import settings


class StartSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        category = request.data.get('category', 'all')
        state = request.data.get('state', 'TX')
        city = request.data.get('city', 'Austin')
        radius_km = int(request.data.get('radius_km', 50))

        search_query = SearchQuery.objects.create(
            seller=request.user,
            category=category,
            state=state,
            city=city,
            radius_km=radius_km,
            status='pending'
        )

        pipeline = DiscoveryPipelineService()
        pipeline.run_search(search_query)

        return Response(SearchQuerySerializer(search_query).data, status=status.HTTP_201_CREATED)


class SearchQueryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queries = SearchQuery.objects.filter(seller=request.user)
        return Response(SearchQuerySerializer(queries, many=True).data)


class SearchQueryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            query = SearchQuery.objects.get(pk=pk, seller=request.user)
            return Response(SearchQuerySerializer(query).data)
        except SearchQuery.DoesNotExist:
            return Response({'error': {'code': 'NOT_FOUND', 'message': 'Search query not found'}}, status=status.HTTP_404_NOT_FOUND)


class BuyerListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Buyer.objects.filter(seller=request.user)
        
        search_id = request.GET.get('search_id')
        if search_id:
            queryset = queryset.filter(search_query_id=search_id)

        email_status = request.GET.get('email_status')
        if email_status:
            queryset = queryset.filter(email_status=email_status)

        has_email = request.GET.get('has_email')
        if has_email == 'true':
            queryset = queryset.exclude(email='')

        serializer = BuyerSerializer(queryset, many=True)
        return Response(serializer.data)


class QuotaUsageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hunter_used = ApiUsage.get_monthly_credits('hunter')
        geoapify_used = ApiUsage.get_daily_credits('geoapify')

        return Response({
            'hunter': {
                'used': hunter_used,
                'limit': settings.HUNTER_MONTHLY_BUDGET,
                'remaining': max(0, settings.HUNTER_MONTHLY_BUDGET - hunter_used)
            },
            'geoapify': {
                'used': geoapify_used,
                'limit': 3000,
                'remaining': max(0, 3000 - geoapify_used)
            }
        })
