from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from ...models import UserModel, UserNotificationSettings


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user profile information with groups and permissions."""

    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "permissions",
            "description",
            "photo",
            "photo_url",
        )
        read_only_fields = (
            "id",
            "date_joined",
            "last_login",
            "is_staff",
            "is_superuser",
        )

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_groups(self, obj):
        """Get user group names efficiently."""
        return list(obj.groups.values_list("name", flat=True))

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_permissions(self, obj):
        """Get all user permissions (group + direct) efficiently."""
        # Get group permissions
        group_perms = set(obj.groups.values_list("permissions__codename", flat=True))
        # Get direct user permissions
        user_perms = set(obj.user_permissions.values_list("codename", flat=True))
        # Combine and return
        return list(group_perms | user_perms)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile information."""

    class Meta:
        model = UserModel
        fields = ("id", "first_name", "last_name", "description")
        read_only_fields = (
            "id",
            "email",
        )  # Email should not be changed via profile update


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user notification settings."""

    class Meta:
        model = UserNotificationSettings
        fields = (
            "id",
            "sms_notifications",
            "push_notifications",
            "email_notifications",
            "task_notifications",
            "specialist_messages",
            "task_updates",
            "marketing_emails",
            "promotional_sms",
            "newsletter",
            "system_alerts",
            "security_notifications",
            "quiet_hours_enabled",
            "quiet_hours_start",
            "quiet_hours_end",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
