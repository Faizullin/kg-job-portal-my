from rest_framework import serializers

from job_portal.apps.core.models import ServiceCategory, ServiceSubcategory
from job_portal.apps.jobs.models import Job
from job_portal.apps.users.models import Master, MasterStatistics
from job_portal.apps.users.api.serializers import (
    UserDetailChildSerializer,
    ProfessionSerializer,
    MasterStatisticsSerializer,
    MasterSkillSerializer,
    PortfolioItemSerializer,
)


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
    """Optimized serializer for master search results."""

    user = UserDetailChildSerializer(read_only=True)
    profession = ProfessionSerializer(read_only=True)
    statistics = serializers.SerializerMethodField()
    skills = MasterSkillSerializer(many=True, read_only=True, source='master_skills')
    portfolio_items = PortfolioItemSerializer(many=True, read_only=True)
    services_offered = ServiceSubcategorySerializer(many=True, read_only=True)
    display_name = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    is_online_display = serializers.SerializerMethodField()

    class Meta:
        model = Master
        fields = [
            "id",
            "user",
            "display_name",
            "profession",
            "statistics",
            "rating",
            "skills",
            "portfolio_items",
            "services_offered",
            "hourly_rate",
            "is_online",
            "is_online_display",
            "current_location",
            "response_time_hours",
            "is_top_master",
            "is_verified_provider",
            "works_remotely",
            "travels_to_clients",
            "accepts_clients_at_location",
        ]

    def get_statistics(self, obj):
        """Get master statistics."""
        try:
            stats = obj.statistics
            return {
                "total_jobs_completed": stats.total_jobs_completed,
                "average_rating": float(stats.average_rating),
                "total_reviews": stats.total_reviews,
                "on_time_percentage": float(stats.on_time_percentage),
                "repeat_customer_percentage": float(stats.repeat_customer_percentage),
            }
        except MasterStatistics.DoesNotExist:
            return {
                "total_jobs_completed": 0,
                "average_rating": 0.0,
                "total_reviews": 0,
                "on_time_percentage": 0.0,
                "repeat_customer_percentage": 0.0,
            }

    def get_display_name(self, obj):
        """Get display name for master."""
        user = obj.user
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name or user.username

    def get_rating(self, obj):
        """Get average rating."""
        try:
            return float(obj.statistics.average_rating)
        except (MasterStatistics.DoesNotExist, AttributeError):
            return 0.0

    def get_is_online_display(self, obj):
        """Get online status display."""
        return "Online" if obj.is_online else "Offline"


class JobSearchSerializer(serializers.ModelSerializer):
    """Optimized serializer for job search results."""

    service_subcategory = ServiceSubcategorySerializer(read_only=True)
    employer_name = serializers.SerializerMethodField()
    employer_avatar = serializers.SerializerMethodField()
    budget_display = serializers.SerializerMethodField()
    urgency_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    time_since_posted = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "status",
            "status_display",
            "employer_name",
            "employer_avatar",
            "service_subcategory",
            "location",
            "city",
            "service_date",
            "service_time",
            "urgency",
            "urgency_display",
            "budget_min",
            "budget_max",
            "budget_display",
            "final_price",
            "special_requirements",
            "time_since_posted",
            "created_at",
        ]

    def get_employer_name(self, obj):
        """Get employer display name."""
        user = obj.employer.user
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name or user.username

    def get_employer_avatar(self, obj):
        """Get employer avatar."""
        return obj.employer.user.photo_url

    def get_budget_display(self, obj):
        """Get formatted budget display."""
        if obj.budget_min and obj.budget_max:
            return f"{obj.budget_min}₸ - {obj.budget_max}₸"
        elif obj.budget_min:
            return f"From {obj.budget_min}₸"
        elif obj.budget_max:
            return f"Up to {obj.budget_max}₸"
        return "Negotiable"

    def get_urgency_display(self, obj):
        """Get urgency display."""
        urgency_map = {
            "low": "Low Priority",
            "medium": "Medium Priority", 
            "high": "High Priority",
            "urgent": "Urgent",
        }
        return urgency_map.get(obj.urgency, "Medium Priority")

    def get_status_display(self, obj):
        """Get status display."""
        status_map = {
            "draft": "Draft",
            "published": "Published",
            "bidding": "Bidding",
            "assigned": "Assigned",
            "in_progress": "In Progress",
            "completed": "Completed",
            "cancelled": "Cancelled",
        }
        return status_map.get(obj.status, "Unknown")

    def get_time_since_posted(self, obj):
        """Get time since job was posted."""
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        now = timezone.now()
        return timesince(obj.created_at, now) + " ago"