from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import UserModel
from utils.serializers import AbstractTimestampedModelSerializer
from job_portal.apps.attachments.models import Attachment
from ..models import (
    Employer,
    Skill,
    PortfolioItem,
    Master, MasterSkill, Certificate, Profession, MasterStatistics,
)


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for generic attachments."""

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'original_filename', 'file_url', 'size', 'file_type', 'mime_type', 'uploaded_by', 'description', 'is_public', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None


class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            "id",
            "username",
            "description",
            "email",
            "first_name",
            "last_name",
            "photo_url",
        )
        read_only_fields = ("id", "photo_url")


class EmployerProfileCreateUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Employer
        fields = ("id", "contact_phone", "preferred_services", "favorite_masters",)
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = self.context['request'].user
        employer_profile, created = Employer.objects.get_or_create(user=user, defaults=validated_data)
        if not created:
            raise ValidationError("Employer profile already exists for this user.")
        preferred_services = validated_data.pop("preferred_services", None)
        favorite_masters = validated_data.pop("favorite_masters", None)
        if preferred_services:
            employer_profile.preferred_services.set(preferred_services)
        if favorite_masters:
            employer_profile.favorite_masters.set(favorite_masters)
        return employer_profile

    def update(self, instance, validated_data):
        preferred_services = validated_data.pop("preferred_services", None)
        favorite_masters = validated_data.pop("favorite_masters", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if preferred_services is not None:
            instance.preferred_services.set(preferred_services)
        if favorite_masters is not None:
            instance.favorite_masters.set(favorite_masters)
        instance.save()
        return instance


class MasterProfileCreateUpdateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Master
        fields = (
            "id",
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
            "is_verified_provider",
            "is_top_master",
        )
        read_only_fields = ("id", "is_verified_provider", "is_top_master")

    def create(self, validated_data):
        user = self.context['request'].user
        master_profile, created = Master.objects.get_or_create(user=user, defaults=validated_data)
        if not created:
            raise ValidationError("Master profile already exists for this user.")
        service_areas = validated_data.pop("service_areas", None)
        services_offered = validated_data.pop("services_offered", None)
        if service_areas:
            master_profile.service_areas.set(service_areas)
        if services_offered:
            master_profile.services_offered.set(services_offered)
        return master_profile

    def update(self, instance, validated_data):
        service_areas = validated_data.pop("service_areas", None)
        services_offered = validated_data.pop("services_offered", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if service_areas is not None:
            instance.service_areas.set(service_areas)
        if services_offered is not None:
            instance.services_offered.set(services_offered)
        instance.save()
        return instance


class SkillDetailSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name", "description", "category", "is_active")
        read_only_fields = ("id",)


class MasterSkillSerializer(AbstractTimestampedModelSerializer):
    skill = SkillDetailSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        source='skill', queryset=Skill.objects.filter(is_active=True),
        write_only=True
    )

    class Meta:
        model = MasterSkill
        fields = (
            "id",
            "skill",
            "skill_id",
            "is_primary_skill",
            "proficiency_level",
            "years_of_experience",
            "created_at",
        )
        read_only_fields = ("id", "created_at",)

    def create(self, validated_data):
        user = self.context['request'].user
        master_profile = user.master_profile
        return MasterSkill.objects.create(
            **validated_data,
            master=master_profile
        )


class PortfolioItemSerializer(AbstractTimestampedModelSerializer):
    skill_used = SkillDetailSerializer(read_only=True)
    skill_used_id = serializers.PrimaryKeyRelatedField(
        source='skill_used', queryset=Skill.objects.filter(is_active=True),
        write_only=True, required=False,
        allow_null=True
    )
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = PortfolioItem
        fields = (
            "id",
            "title",
            "description",
            "skill_used",
            "skill_used_id",
            "is_featured",
            "attachments",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        user = self.context['request'].user
        master_profile = user.master_profile
        return PortfolioItem.objects.create(
            **validated_data,
            master=master_profile
        )


class CertificateSerializer(AbstractTimestampedModelSerializer):
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
        read_only_fields = ("id", "is_verified",)

    def create(self, validated_data):
        user = self.context['request'].user
        master_profile = user.master_profile
        return Certificate.objects.create(
            **validated_data,
            master=master_profile
        )


class ProfessionSerializer(AbstractTimestampedModelSerializer):
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


class MasterStatisticsSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = MasterStatistics
        fields = (
            "id",
            "total_jobs_completed",
            "on_time_percentage",
            "repeat_customer_percentage",
            "average_rating",
            "total_reviews",
        )


class PublicMasterProfileSerializer(serializers.ModelSerializer):
    user = UserDetailChildSerializer(read_only=True)
    profession = ProfessionSerializer(read_only=True)

    class Meta:
        model = Master
        fields = (
            "id",
            "user",
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
            "is_online",
            "last_seen",
            "is_verified_provider",
            "is_top_master",
            "profession",
        )


class PublicMasterProfileDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for master profile."""

    user = UserDetailChildSerializer(read_only=True)
    profession = ProfessionSerializer(read_only=True)
    skills = MasterSkillSerializer(many=True, read_only=True)
    portfolio_items = PortfolioItemSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    statistics = MasterStatisticsSerializer(read_only=True)

    class Meta:
        model = Master
        fields = (
            "id",
            "user",
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
            "is_online",
            "last_seen",
            "is_verified_provider",
            "is_top_master",

            "profession",
            "skills",
            "portfolio_items",
            "certificates",
            "statistics",
        )


class MasterOnlineStatusRequestSerializer(serializers.Serializer):
    """Serializer for master online status update request."""
    
    is_online = serializers.BooleanField(help_text="Online status to set", default=False)


class MasterOnlineStatusResponseSerializer(serializers.Serializer):
    """Serializer for master online status update response."""
    
    message = serializers.CharField(help_text="Success message")
    is_online = serializers.BooleanField(help_text="Current online status")
    last_seen = serializers.DateTimeField(help_text="Last seen timestamp")
