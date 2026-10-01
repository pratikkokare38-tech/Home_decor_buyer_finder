from rest_framework import serializers
from apps.buyers.models import SearchQuery, Buyer


class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = [
            'id', 'business_name', 'category', 'website', 'domain',
            'email', 'email_source', 'email_status', 'phone', 'address',
            'city', 'state', 'lat', 'lon', 'source_api', 'created_at'
        ]


class SearchQuerySerializer(serializers.ModelSerializer):
    buyers_count = serializers.IntegerField(source='buyers.count', read_only=True)

    class Meta:
        model = SearchQuery
        fields = [
            'id', 'category', 'state', 'city', 'radius_km',
            'status', 'total_found', 'error_message', 'buyers_count', 'created_at'
        ]
