from rest_framework import serializers
from utils.serializers import AbstractTimestampedModelSerializer
from ..models import (
    UserProfile, ServiceProviderProfile, ClientProfile, 
    MasterSkill, ServiceProviderSkill, PortfolioItem, Certificate,
    Profession, ProviderStatistics
)
from accounts.api.serializers.user_serializers import UserProfileSerializer, UserUpdateSerializer
from job_portal.apps.core.models import ServiceSubcategory

class ServiceProviderSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceProviderProfile
        fields = (
            'id', 'user_profile',
            'business_name', 'business_description', 'profession',
            'service_areas', 'services_offered',
            'works_remotely', 'accepts_clients_at_location', 'travels_to_clients',
            'is_available', 'hourly_rate', 'response_time_hours',
            'work_experience_start_year', 'education_institution', 'education_years', 'languages',
            'about_description', 'current_location', 'is_online', 'last_seen',
            'is_verified_provider', 'is_top_master',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'is_verified_provider', 'is_top_master', 'created_at', 'updated_at'
        )


class PreferredServiceSubcategorySerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceSubcategory
        fields = ('id', 'name', 'description', 'icon', 'is_active', 'featured', 'base_price', 'price_range_min', 'price_range_max', 'estimated_duration', 'complexity_level', 'safety_requirements', 'slug', 'meta_title', 'meta_description')

class ClientSerializer(AbstractTimestampedModelSerializer):
    preferred_services = PreferredServiceSubcategorySerializer(many=True, read_only=True)

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
            'user',
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
            'bio', 'date_of_birth', 'gender',
            'phone_number', 'address', 'city', 'state', 'country', 'postal_code',
            'preferred_language', 'notification_preferences',
        )


class ServiceProviderUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceProviderProfile
        fields = (
            'business_name', 'business_description', 'profession',
            'service_areas', 'services_offered',
            'works_remotely', 'accepts_clients_at_location', 'travels_to_clients',
            'is_available', 'hourly_rate', 'response_time_hours',
            'work_experience_start_year', 'education_institution', 'education_years', 'languages',
            'about_description', 'current_location',
        )
        read_only_fields = ('is_verified_provider', 'is_top_master')


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


# New serializers for mobile app features
class MasterSkillSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = MasterSkill
        fields = ('id', 'name', 'description', 'category', 'is_active', 'created_at', 'updated_at')


class ServiceProviderSkillSerializer(AbstractTimestampedModelSerializer):
    skill = MasterSkillSerializer(read_only=True)
    skill_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ServiceProviderSkill
        fields = ('id', 'skill', 'skill_id', 'proficiency_level', 'years_of_experience', 'is_primary_skill', 'created_at', 'updated_at')


class PortfolioItemSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = (
            'id', 'service_provider', 'title', 'description', 'image',
            'skill_used', 'is_featured', 'created_at', 'updated_at'
        )
        read_only_fields = ('service_provider', 'created_at', 'updated_at')


class CertificateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Certificate
        fields = (
            'id', 'service_provider', 'name', 'issuing_organization', 'certificate_number',
            'issue_date', 'expiry_date', 'certificate_file', 'is_verified', 'created_at', 'updated_at'
        )
        read_only_fields = ('service_provider', 'created_at', 'updated_at')


class ProfessionSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Profession
        fields = ('id', 'name', 'description', 'category', 'is_active', 'created_at', 'updated_at')


class ProviderStatisticsSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ProviderStatistics
        fields = (
            'id', 'provider', 'total_jobs_completed', 'on_time_percentage', 
            'repeat_customer_percentage', 'average_rating', 'total_reviews', 'created_at', 'updated_at'
        )
        read_only_fields = ('provider', 'created_at', 'updated_at')




# Enhanced serializers for mobile app
class ServiceProviderDetailSerializer(ServiceProviderSerializer):
    """Enhanced serializer for detailed provider view with related data."""
    provider_skills = ServiceProviderSkillSerializer(many=True, read_only=True)
    portfolio_items = PortfolioItemSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    statistics = ProviderStatisticsSerializer(read_only=True)
    
    class Meta(ServiceProviderSerializer.Meta):
        fields = ServiceProviderSerializer.Meta.fields + ('provider_skills', 'portfolio_items', 'certificates', 'statistics')




