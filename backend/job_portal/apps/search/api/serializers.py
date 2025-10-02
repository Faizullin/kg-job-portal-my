from rest_framework import serializers
from django.contrib.auth import get_user_model

from job_portal.apps.attachments.serializers import AttachmentSerializer
from job_portal.apps.core.models import ServiceCategory, ServiceSubcategory
from job_portal.apps.jobs.models import Job
from job_portal.apps.users.models import Master, MasterStatistics, Profession, PortfolioItem
from job_portal.apps.users.api.serializers import MasterStatisticsSerializer, UserDetailChildSerializer, MasterSkillSerializer

UserModel = get_user_model()


class ProfessionBasicSerializer(serializers.ModelSerializer):
    """Basic profession information."""
    
    class Meta:
        model = Profession
        fields = ["id", "name"]


class ServiceCategoryBasicSerializer(serializers.ModelSerializer):
    """Basic service category information."""
    
    class Meta:
        model = ServiceCategory
        fields = [
            "id",
            "name",
            "icon",
            "color",
            "banner_image",
        ]


class PortfolioItemBasicSerializer(serializers.ModelSerializer):
    """Basic portfolio item serializer."""

    attachments = AttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = PortfolioItem
        fields = [
            "id",
            "title",
            "attachments",
            "description",
        ]


class ServiceSubcategoryBasicSerializer(serializers.ModelSerializer):
    """Basic service subcategory serializer."""
    
    class Meta:
        model = ServiceSubcategory
        fields = [
            "id",
            "name",
        ]


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for service categories in search results."""

    class Meta:
        model = ServiceCategory
        fields = [
            "id",
            "name",
            "icon",
            "color",
            "description",
        ]


class ServiceSubcategorySerializer(serializers.ModelSerializer):
    """Serializer for service subcategories in search results."""

    category = ServiceCategorySerializer(read_only=True)

    class Meta:
        model = ServiceSubcategory
        fields = ["id", "name", "category"]


class MasterSearchSerializer(serializers.ModelSerializer):
    """Enhanced serializer for master search results matching the image requirements."""

    user = UserDetailChildSerializer(read_only=True)
    profession = ProfessionBasicSerializer(read_only=True)
    statistics = MasterStatisticsSerializer(read_only=True)
    services_offered = ServiceSubcategoryBasicSerializer(many=True, read_only=True)
    master_skills = MasterSkillSerializer(many=True, read_only=True)
    portfolio_items = PortfolioItemBasicSerializer(many=True, read_only=True)

    class Meta:
        model = Master
        fields = [
            "id",
            "user",
            "profession",
            "statistics",
            "services_offered",
            "master_skills",
            "portfolio_items",
            "hourly_rate",
            "is_online",
            "current_location",
            "response_time_hours",
            "is_top_master",
            "is_verified_provider",
            "works_remotely",
            "travels_to_clients",
            "accepts_clients_at_location",
        ]


class JobSearchSerializer(serializers.ModelSerializer):
    """Simplified serializer for job search results using nested serializers."""

    service_subcategory = ServiceSubcategorySerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "status",
            "service_subcategory",
            "location",
            "city",
            "service_date",
            "service_time",
            "urgency",
            "budget_min",
            "budget_max",
            "final_price",
            "special_requirements",
            "created_at",
        ]


# Recommendation System Serializers
class MasterRecommendationSerializer(serializers.ModelSerializer):
    """Optimized serializer for master recommendations."""
    
    user = UserDetailChildSerializer(read_only=True)
    profession = ProfessionBasicSerializer(read_only=True)
    statistics = MasterStatisticsSerializer(read_only=True)
    services_offered = ServiceSubcategoryBasicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Master
        fields = [
            "id", 
            "user",
            "profession",
            "statistics",
            "services_offered",
            "hourly_rate",
            "is_online",
            "current_location",
            "response_time_hours",
            "is_verified_provider",
            "is_top_master",
            "works_remotely",
            "travels_to_clients",
        ]


class ServiceCategoryWithCountSerializer(serializers.ModelSerializer):
    """Service category with master count for home page."""
    
    master_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ServiceCategory
        fields = [
            "id",
            "name",
            "icon",
            "color",
            "banner_image",
            "master_count",
        ]


class HomePageDataSerializer(serializers.Serializer):
    """Comprehensive serializer for home page data with proper OpenAPI documentation."""
    
    featured_categories = ServiceCategoryWithCountSerializer(many=True, help_text="Featured service categories")
    recommended_masters = MasterRecommendationSerializer(many=True, help_text="Recommended masters for the user")
    user_location = serializers.CharField(help_text="Current user location")
    total_masters_count = serializers.IntegerField(help_text="Total number of available masters")
    total_jobs_count = serializers.IntegerField(help_text="Total number of published jobs")
    
    class Meta:
        # This helps OpenAPI understand the response structure
        ref_name = "HomePageData"

