from rest_framework import serializers
from utils.serializers import AbstractTimestampedModelSerializer
from ..models import UserProfile, ServiceProviderProfile, ClientProfile
from accounts.api.serializers.user_serializers import UserProfileSerializer, UserUpdateSerializer


class ServiceProviderSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceProviderProfile
        fields = (
            'id', 'user_profile',
            'business_name', 'business_description',
            'service_areas', 'services_offered',
            'works_remotely', 'accepts_clients_at_location', 'travels_to_clients',
            'is_available',
            'average_rating', 'total_reviews',
            'is_verified_provider',
            'created_at', 'updated_at',
        )
        read_only_fields = ('average_rating', 'total_reviews', 'is_verified_provider', 'created_at', 'updated_at')


class ClientSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ClientProfile
        fields = (
            'id', 'user_profile',
            'preferred_services',
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
            'terms_accepted', 'terms_accepted_at',
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
            'business_name', 'business_description',
            'service_areas', 'services_offered',
            'works_remotely', 'accepts_clients_at_location', 'travels_to_clients',
            'is_available',
        )
        read_only_fields = ('is_verified_provider',)


class ClientUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ClientProfile
        fields = (
            'preferred_services',
        )


class AdvancedProfileSerializer(serializers.Serializer):
    """Combined serializer for user account data and job portal profile."""
    user_data = UserProfileSerializer(read_only=True)
    job_portal_profile = UserProfileDetailSerializer(read_only=True)
    
    def to_representation(self, instance):
        """Combine user data and job portal profile data."""
        user_data = UserProfileSerializer(instance).data
        job_portal_profile = None
        
        # Get job portal profile if it exists
        try:
            if hasattr(instance, 'job_portal_profile'):
                job_portal_profile = UserProfileDetailSerializer(instance.job_portal_profile).data
        except UserProfile.DoesNotExist:
            pass
        
        return {
            'user_data': user_data,
            'job_portal_profile': job_portal_profile
        }


class AdvancedProfileUpdateSerializer(serializers.Serializer):
    """Combined serializer for updating both user account and job portal profile."""
    user_data = UserUpdateSerializer(required=False)
    job_portal_profile = UserProfileUpdateSerializer(required=False)
    
    def update(self, instance, validated_data):
        """Update both user account and job portal profile."""
        user_data = validated_data.get('user_data', {})
        job_portal_data = validated_data.get('job_portal_profile', {})
        
        # Update user account data
        if user_data:
            user_serializer = UserUpdateSerializer(instance, data=user_data, partial=True)
            if user_serializer.is_valid():
                instance = user_serializer.save()
        
        # Update job portal profile data
        if job_portal_data:
            try:
                job_portal_profile = instance.job_portal_profile
                profile_serializer = UserProfileUpdateSerializer(job_portal_profile, data=job_portal_data, partial=True)
                if profile_serializer.is_valid():
                    profile_serializer.save()
            except UserProfile.DoesNotExist:
                # Create job portal profile if it doesn't exist
                job_portal_data['user'] = instance
                profile_serializer = UserProfileUpdateSerializer(data=job_portal_data)
                if profile_serializer.is_valid():
                    profile_serializer.save()
        
        return instance
