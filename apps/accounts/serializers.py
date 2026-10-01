from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SellerProfile


class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ['id', 'company_name', 'website', 'product_categories', 'from_name', 'from_email', 'postal_address']


class UserSerializer(serializers.ModelSerializer):
    seller_profile = SellerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'seller_profile']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    company_name = serializers.CharField(max_length=255)
    from_name = serializers.CharField(max_length=150)
    postal_address = serializers.CharField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        profile, _ = SellerProfile.objects.get_or_create(user=user)
        profile.company_name = validated_data['company_name']
        profile.from_name = validated_data['from_name']
        profile.from_email = validated_data['email']
        profile.postal_address = validated_data['postal_address']
        profile.save()
        return user
