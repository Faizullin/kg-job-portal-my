from rest_framework import serializers

from ...models import UserModel, UserNotificationSettings


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user profile information - enhanced version of api_users"""

    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser',
            'groups', 'permissions', 'description',
            'photo', 'photo_url'
        )
        read_only_fields = ('id', 'date_joined', 'last_login', 'is_staff', 'is_superuser')

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]

    def get_permissions(self, obj):
        group_permissions = set()
        for group in obj.groups.all():
            for permission in group.permissions.all():
                group_permissions.add(permission.codename)

        user_permissions = set()
        for permission in obj.user_permissions.all():
            user_permissions.add(permission.codename)

        return list(group_permissions | user_permissions)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile - enhanced version of api_users EditUserSettingsView"""

    class Meta:
        model = UserModel
        fields = ('email', 'description', 'photo_url', 'first_name', 'last_name')
        read_only_fields = ('email',)  # Email should not be changed via profile update


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user notification settings."""

    class Meta:
        model = UserNotificationSettings
        fields = (
            'id', 'sms_notifications', 'push_notifications', 'email_notifications',
            'task_notifications', 'specialist_messages', 'task_updates',
            'marketing_emails', 'promotional_sms', 'newsletter',
            'system_alerts', 'security_notifications',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
