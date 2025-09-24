from rest_framework import serializers
from utils.serializers import AbstractTimestampedModelSerializer
from ..models import ServiceProviderProfile, ClientProfile, UserProfile
from ..models_enhanced import (
    PricingStructure, ProfessionalInformation, ProviderLanguage, 
    Certificate, WorkPortfolio, AvailabilityStatus, UserPreference,
    RecommendationEngine, StatisticsAggregation, Language
)


class PricingStructureSerializer(AbstractTimestampedModelSerializer):
    service_name = serializers.CharField(source='service_subcategory.name', read_only=True)
    category_name = serializers.CharField(source='service_subcategory.category.name', read_only=True)
    
    class Meta:
        model = PricingStructure
        fields = [
            'id', 'service_subcategory', 'service_name', 'category_name',
            'hourly_rate', 'daily_rate', 'per_order_rate', 'minimum_charge',
            'currency', 'is_negotiable', 'includes_materials'
        ]


class ProfessionalInformationSerializer(AbstractTimestampedModelSerializer):
    education_level_display = serializers.CharField(source='get_education_level_display', read_only=True)
    
    class Meta:
        model = ProfessionalInformation
        fields = [
            'id', 'years_of_experience', 'work_experience_description',
            'education_level', 'education_level_display', 'education_institution',
            'education_field', 'graduation_year', 'specializations', 'tools_and_equipment'
        ]


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'code']


class ProviderLanguageSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(source='language.name', read_only=True)
    proficiency_display = serializers.CharField(source='get_proficiency_level_display', read_only=True)
    
    class Meta:
        model = ProviderLanguage
        fields = ['id', 'language', 'language_name', 'proficiency_level', 'proficiency_display']


class CertificateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Certificate
        fields = [
            'id', 'name', 'issuing_organization', 'issue_date', 'expiry_date',
            'certificate_number', 'certificate_file', 'certificate_url',
            'is_verified', 'verified_at'
        ]


class WorkPortfolioSerializer(AbstractTimestampedModelSerializer):
    service_name = serializers.CharField(source='service_category.name', read_only=True)
    category_name = serializers.CharField(source='service_category.category.name', read_only=True)
    
    class Meta:
        model = WorkPortfolio
        fields = [
            'id', 'title', 'description', 'service_category', 'service_name', 'category_name',
            'image', 'image_url', 'video_url', 'completion_date', 'client_feedback',
            'is_featured', 'is_public'
        ]


class AvailabilityStatusSerializer(AbstractTimestampedModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AvailabilityStatus
        fields = [
            'id', 'status', 'status_display', 'current_order', 'estimated_completion',
            'current_location', 'is_location_accurate', 'last_location_update',
            'working_hours_start', 'working_hours_end', 'working_days'
        ]


class ServiceProviderEnhancedSerializer(AbstractTimestampedModelSerializer):
    """Enhanced serializer for service providers with all related data."""
    
    # Basic provider info
    user_name = serializers.CharField(source='user_profile.user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user_profile.user.username', read_only=True)
    user_email = serializers.CharField(source='user_profile.user.email', read_only=True)
    user_photo = serializers.CharField(source='user_profile.user.photo_url', read_only=True)
    city = serializers.CharField(source='user_profile.city', read_only=True)
    phone_number = serializers.CharField(source='user_profile.phone_number', read_only=True)
    
    # Related data
    pricing_structures = PricingStructureSerializer(many=True, read_only=True)
    professional_info = ProfessionalInformationSerializer(read_only=True)
    languages = ProviderLanguageSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    portfolio_items = WorkPortfolioSerializer(many=True, read_only=True)
    availability_status = AvailabilityStatusSerializer(read_only=True)
    
    # Service information
    services_offered_names = serializers.SerializerMethodField()
    service_areas_names = serializers.SerializerMethodField()
    
    # Performance metrics
    performance_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceProviderProfile
        fields = [
            'id', 'business_name', 'business_description', 'is_available',
            'is_verified_provider', 'average_rating', 'total_reviews',
            'works_remotely', 'accepts_clients_at_location', 'travels_to_clients',
            
            # User info
            'user_name', 'user_username', 'user_email', 'user_photo',
            'city', 'phone_number',
            
            # Related data
            'pricing_structures', 'professional_info', 'languages',
            'certificates', 'portfolio_items', 'availability_status',
            
            # Service info
            'services_offered_names', 'service_areas_names',
            
            # Performance
            'performance_stats',
        ]
    
    def get_services_offered_names(self, obj):
        return [service.name for service in obj.services_offered.all()]
    
    def get_service_areas_names(self, obj):
        return [area.name for area in obj.service_areas.all()]
    
    def get_performance_stats(self, obj):
        return {
            'completed_orders': obj.assignments.count(),
            'total_reviews': obj.total_reviews,
            'average_rating': float(obj.average_rating),
            'positive_reviews_percentage': self._calculate_positive_reviews_percentage(obj),
            'repeat_customers_percentage': 45.0,  # Placeholder
        }
    
    def _calculate_positive_reviews_percentage(self, provider):
        """Calculate percentage of positive reviews (4+ stars)."""
        positive_reviews = provider.reviews_received.filter(overall_rating__gte=4).count()
        total_reviews = provider.reviews_received.count()
        return round((positive_reviews / total_reviews * 100) if total_reviews > 0 else 0, 1)


class UserPreferenceSerializer(AbstractTimestampedModelSerializer):
    preferred_categories_names = serializers.SerializerMethodField()
    preferred_subcategories_names = serializers.SerializerMethodField()
    preferred_providers_names = serializers.SerializerMethodField()
    
    class Meta:
        model = UserPreference
        fields = [
            'id', 'preferred_categories', 'preferred_categories_names',
            'preferred_subcategories', 'preferred_subcategories_names',
            'preferred_providers', 'preferred_providers_names',
            'preferred_cities', 'max_distance_km',
            'budget_range_min', 'budget_range_max',
            'min_rating_preference', 'prefer_verified_providers'
        ]
    
    def get_preferred_categories_names(self, obj):
        return [cat.name for cat in obj.preferred_categories.all()]
    
    def get_preferred_subcategories_names(self, obj):
        return [sub.name for sub in obj.preferred_subcategories.all()]
    
    def get_preferred_providers_names(self, obj):
        return [f"{prov.user_profile.user.get_full_name()}" for prov in obj.preferred_providers.all()]


class RecommendationSerializer(AbstractTimestampedModelSerializer):
    recommendation_type_display = serializers.CharField(source='get_recommendation_type_display', read_only=True)
    
    class Meta:
        model = RecommendationEngine
        fields = [
            'id', 'recommendation_type', 'recommendation_type_display',
            'recommended_object_type', 'recommended_object_id',
            'confidence_score', 'reason', 'algorithm_version',
            'is_viewed', 'is_clicked', 'is_dismissed',
            'viewed_at', 'clicked_at'
        ]


class StatisticsAggregationSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = StatisticsAggregation
        fields = [
            'id', 'date', 'total_providers', 'active_providers', 'verified_providers',
            'average_provider_rating', 'total_clients', 'active_clients',
            'total_orders', 'completed_orders', 'cancelled_orders', 'average_order_value',
            'total_reviews', 'average_review_rating', 'total_searches', 'searches_with_results'
        ]


class DashboardStatisticsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    
    user_statistics = serializers.DictField()
    global_statistics = serializers.DictField()
    recommendations = serializers.ListField()


class ProviderSearchResponseSerializer(serializers.Serializer):
    """Serializer for enhanced provider search response."""
    
    results = ServiceProviderEnhancedSerializer(many=True)
    statistics = serializers.DictField()
    pagination = serializers.DictField()


class RecommendationResponseSerializer(serializers.Serializer):
    """Serializer for recommendation response."""
    
    recommendations = serializers.ListField()
    user_preferences = serializers.DictField()
