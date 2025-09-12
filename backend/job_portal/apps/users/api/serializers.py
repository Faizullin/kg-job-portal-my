from rest_framework import serializers
from django.contrib.auth import get_user_model
from utils.serializers import AbstractTimestampedModelSerializer
from utils.abstract_models import AbstractTimestampedModel
from ..models import UserProfile, ServiceProviderProfile, ClientProfile, UserVerification, ServiceProviderService


class ServiceProviderSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceProviderProfile
        fields = (
            'id', 'user_profile',
            'business_name', 'business_description', 'business_license',
            'years_of_experience',
            'service_areas', 'travel_radius',
            'is_available', 'availability_schedule',
            'average_rating', 'total_reviews',
            'is_verified_provider', 'verification_documents',
            'created_at', 'updated_at',
        )
        read_only_fields = ('average_rating', 'total_reviews', 'is_verified_provider', 'created_at', 'updated_at')


class ClientSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ClientProfile
        fields = (
            'id', 'user_profile',
            'preferred_service_areas', 'budget_preferences',
            'total_orders', 'completed_orders', 'cancelled_orders',
            'favorite_providers',
            'created_at', 'updated_at',
        )
        read_only_fields = ('total_orders', 'completed_orders', 'cancelled_orders', 'created_at', 'updated_at')


class UserProfileDetailSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'id',
            'user', 'user_type',
            'bio', 'date_of_birth', 'gender',
            'phone_number', 'address', 'city', 'state', 'country', 'postal_code',
            'preferred_language', 'notification_preferences',
            'is_verified', 'verification_date',
            'created_at', 'updated_at',
        )
        read_only_fields = ('user', 'is_verified', 'verification_date', 'created_at', 'updated_at')


class UserProfileUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'user_type',
            'bio', 'date_of_birth', 'gender',
            'phone_number', 'address', 'city', 'state', 'country', 'postal_code',
            'preferred_language', 'notification_preferences',
        )


class ServiceProviderUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceProviderProfile
        fields = (
            'business_name', 'business_description', 'business_license',
            'years_of_experience',
            'service_areas', 'travel_radius',
            'is_available', 'availability_schedule',
            'verification_documents',
        )


class ClientUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ClientProfile
        fields = (
            'preferred_service_areas', 'budget_preferences',
        )
