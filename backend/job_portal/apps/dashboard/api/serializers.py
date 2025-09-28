from rest_framework import serializers

from job_portal.apps.core.models import ServiceCategory, ServiceSubcategory
from job_portal.apps.users.api.serializers import (
    AdvancedUserProfileRetrieveUpdateSerializer,
    PortfolioItemCreateUpdateSerializer,
    ProfessionSerializer,
    ProviderStatisticsSerializer,
)
from job_portal.apps.users.models import (
    Skill,
    ProviderStatistics,
    ServiceProviderProfile,
    ServiceProviderSkill,
    UserProfile,
)


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for service categories in dashboard."""

    class Meta:
        model = ServiceCategory
        fields = [
            "id",
            "name",
            "icon",
            "color",
            "description",
            "featured",
            "sort_order",
        ]


class ServiceSubcategorySerializer(serializers.ModelSerializer):
    """Serializer for service subcategories."""

    category = ServiceCategorySerializer(read_only=True)

    class Meta:
        model = ServiceSubcategory
        fields = ["id", "name", "category"]


class ServiceProviderProfileSerializer(serializers.ModelSerializer):
    """Nested serializer for service provider profile data."""

    user_profile = AdvancedUserProfileRetrieveUpdateSerializer(read_only=True)
    profession = ProfessionSerializer(read_only=True)
    statistics = ProviderStatisticsSerializer(read_only=True)

    class Meta:
        model = ServiceProviderProfile
        fields = [
            "id",
            "user_profile",
            "profession",
            "statistics",
            "hourly_rate",
            "is_online",
            "current_location",
            "response_time_hours",
            "is_top_master",
            "is_verified_provider",
        ]


class MasterSkillSerializer(serializers.ModelSerializer):
    """Serializer for master skills."""

    class Meta:
        model = Skill
        fields = ["id", "name", "description"]


class ServiceProviderSkillSerializer(serializers.ModelSerializer):
    """Serializer for service provider skills with nested skill data."""

    skill = MasterSkillSerializer(read_only=True)

    class Meta:
        model = ServiceProviderSkill
        fields = [
            "id",
            "skill",
            "proficiency_level",
            "years_of_experience",
            "is_primary_skill",
        ]


class ServiceProviderSearchListSerializer(serializers.ModelSerializer):
    """Serializer for service provider search results - detailed fields for search page."""

    profession = ProfessionSerializer(read_only=True)
    statistics = ProviderStatisticsSerializer(read_only=True)
    provider_skills = ServiceProviderSkillSerializer(many=True, read_only=True)
    portfolio_items = PortfolioItemCreateUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceProviderProfile
        fields = [
            "id",
            "profession",
            "statistics",
            "provider_skills",
            "portfolio_items",
            "hourly_rate",
            "is_online",
            "current_location",
            "response_time_hours",
            "is_top_master",
            "is_verified_provider",
        ]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders in dashboard."""

    service_subcategory = ServiceSubcategorySerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "title",
            "status",
            "created_at",
            "budget_min",
            "budget_max",
            "final_price",
            "urgency",
            "city",
            "service_subcategory",
        ]


class PlatformStatsSerializer(serializers.Serializer):
    """Serializer for platform statistics."""

    total_providers = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    average_rating = serializers.FloatField()
    response_time_hours = serializers.IntegerField()


class ClientDashboardResponseSerializer(serializers.Serializer):
    """Serializer for client dashboard response."""

    featured_categories = ServiceCategorySerializer(many=True)
    top_providers = ServiceProviderProfileSerializer(many=True)
    recent_orders = OrderSerializer(many=True)
    platform_stats = PlatformStatsSerializer()

# class ClientUserSerializer(serializers.ModelSerializer):
#     """Serializer for client user data."""

#     class Meta:
#         model = UserModel
#         fields = ["id", "first_name", "last_name", "username", "photo_url"]


# class ReviewSerializer(serializers.ModelSerializer):
#     """Serializer for reviews in provider dashboard."""

#     reviewer = ClientUserSerializer(read_only=True)

#     class Meta:
#         model = Review
#         fields = [
#             "id",
#             "reviewer",
#             "overall_rating",
#             "comment",
#             "created_at",
#             "title",
#             "is_verified",
#         ]


# class CertificateSerializer(serializers.ModelSerializer):
#     """Serializer for certificates."""

#     class Meta:
#         model = Certificate
#         fields = [
#             "id",
#             "name",
#             "issuing_organization",
#             "certificate_number",
#             "issue_date",
#             "expiry_date",
#             "certificate_file",
#             "is_verified",
#         ]


# class ProviderDashboardResponseSerializer(serializers.Serializer):
#     """Serializer for provider dashboard response."""

#     provider_info = ServiceProviderProfileSerializer(read_only=True)
#     statistics = ProviderStatisticsSerializer(read_only=True)
#     recent_reviews = ReviewSerializer(many=True)
#     skills = ServiceProviderSkillSerializer(many=True)
#     certificates = CertificateSerializer(many=True)
