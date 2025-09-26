from accounts.api.serializers.user_serializers import (
    UserDetailSerializer,
    UserUpdateSerializer,
)
from accounts.models import UserModel
from job_portal.apps.core.api.serializers import (
    ServiceAreaSerializer,
    ServiceSubcategorySerializer,
)
from rest_framework import serializers
from utils.serializers import AbstractTimestampedModelSerializer

from ..models import (
    Certificate,
    ClientProfile,
    MasterSkill,
    PortfolioItem,
    Profession,
    ProviderStatistics,
    ServiceProviderProfile,
    ServiceProviderSkill,
    UserProfile,
)


class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("id", "username", "description", "email", "first_name", "last_name", "photo_url")
        read_only_fields = ("id", "photo_url")


class AdvancedUserProfileRetrieveUpdateSerializer(serializers.ModelSerializer):
    user = UserRetrieveUpdateSerializer()

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "bio",
            "date_of_birth",
            "gender",
            "phone_number",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "terms_accepted",
            "terms_accepted_at",
            "preferred_language",
            "notification_preferences",
            "is_verified",
            "verification_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "user",
            "is_verified",
            "verification_date",
            "created_at",
            "updated_at",
        )


class ClientProfileCreateUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ("preferred_services",)


class ServiceProviderProfileUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceProviderProfile
        fields = (
            "business_name",
            "business_description",
            "profession",
            "service_areas",
            "services_offered",
            "works_remotely",
            "accepts_clients_at_location",
            "travels_to_clients",
            "is_available",
            "hourly_rate",
            "response_time_hours",
            "work_experience_start_year",
            "education_institution",
            "education_years",
            "languages",
            "about_description",
            "current_location",
        )
        read_only_fields = ("is_verified_provider", "is_top_master")


class MasterSkillDetailSerializer(AbstractTimestampedModelSerializer):
    """Serializer for listing available skills."""

    class Meta:
        model = MasterSkill
        fields = ("id", "name", "description", "category", "is_active")


class ServiceProviderSkillDetailSerializer(AbstractTimestampedModelSerializer):
    """Serializer for service provider skills (list/detail)."""

    skill = MasterSkillDetailSerializer(read_only=True)

    class Meta:
        model = ServiceProviderSkill
        fields = (
            "id",
            "skill",
            "is_primary_skill",
            "proficiency_level",
            "years_of_experience",
        )


class ServiceProviderSkillCreateUpdateSerializer(AbstractTimestampedModelSerializer):
    """Serializer for creating/updating service provider skills."""

    class Meta:
        model = ServiceProviderSkill
        fields = (
            "skill",
            "is_primary_skill",
            "proficiency_level",
            "years_of_experience",
        )


class PortfolioItemDetailSerializer(AbstractTimestampedModelSerializer):
    """Serializer for portfolio items (list/detail)."""

    skill_used = MasterSkillDetailSerializer(read_only=True)

    class Meta:
        model = PortfolioItem
        fields = (
            "id",
            "title",
            "description",
            "skill_used",
            "is_featured",
            "image",
            "created_at",
        )


class PortfolioItemCreateUpdateSerializer(AbstractTimestampedModelSerializer):
    """Serializer for creating/updating portfolio items."""

    class Meta:
        model = PortfolioItem
        fields = ("title", "description", "skill_used", "is_featured", "image")


class CertificateDetailSerializer(AbstractTimestampedModelSerializer):
    """Serializer for certificates (list/detail)."""

    class Meta:
        model = Certificate
        fields = (
            "id",
            "name",
            "issuing_organization",
            "issue_date",
            "expiry_date",
            "certificate_number",
            "certificate_file",
            "is_verified",
        )


class CertificateCreateUpdateSerializer(AbstractTimestampedModelSerializer):
    """Serializer for creating/updating certificates."""

    class Meta:
        model = Certificate
        fields = (
            "name",
            "issuing_organization",
            "issue_date",
            "expiry_date",
            "certificate_number",
            "certificate_file",
        )


class ProviderStatisticsSerializer(AbstractTimestampedModelSerializer):
    """Serializer for provider statistics."""

    class Meta:
        model = ProviderStatistics
        fields = (
            "average_rating",
            "total_reviews",
            "total_jobs_completed",
            "on_time_percentage",
            "repeat_customer_percentage",
        )


class ProfessionSerializer(AbstractTimestampedModelSerializer):
    """Serializer for listing professions."""

    class Meta:
        model = Profession
        fields = (
            "id",
            "name",
        )


class UserDetailChildSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = UserModel
        fields = ("id", "username", "email", "first_name", "last_name", "photo_url")
        read_only_fields = ("id", "photo_url")


class UserPrfileWrapSerializer(serializers.ModelSerializer):
    user = UserDetailChildSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "bio",
            "date_of_birth",
            "gender",
            "phone_number",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "terms_accepted",
            "terms_accepted_at",
            "preferred_language",
            "notification_preferences",
            "is_verified",
            "verification_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "is_verified",
            "verification_date",
            "created_at",
            "updated_at",
        )


class ServiceProviderProfileDetailSerializer(serializers.ModelSerializer):
    """Enhanced serializer for detailed provider view with related data."""

    user_profile = AdvancedUserProfileRetrieveUpdateSerializer(read_only=True)
    provider_skills = ServiceProviderSkillDetailSerializer(many=True, read_only=True)
    portfolio_items = PortfolioItemDetailSerializer(many=True, read_only=True)
    certificates = CertificateDetailSerializer(many=True, read_only=True)
    statistics = ProviderStatisticsSerializer(read_only=True)
    profession = ProfessionSerializer(read_only=True)

    class Meta:
        model = ServiceProviderProfile
        fields = (
            "id",
            "user_profile",
            "provider_skills",
            "portfolio_items",
            "certificates",
            "statistics",
            "profession",
            "is_available",
            "is_verified_provider",
            "is_top_master",
            "business_name",
            "business_description",
            "works_remotely",
            "accepts_clients_at_location",
            "travels_to_clients",
            "hourly_rate",
            "response_time_hours",
            "work_experience_start_year",
            "education_institution",
            "education_years",
            "languages",
            "about_description",
            "current_location",
            "is_online",
            "last_seen",
        )
