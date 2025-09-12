from rest_framework import serializers
from ...models import UserModel


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information - enhanced version of api_users"""
    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = UserModel
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser',
            'groups', 'permissions', 'name', 'description', 
            'photo', 'photo_url', 'timezone_difference', 'points', 'day_streak', 'max_day_streak'
        )
        read_only_fields = ('id', 'date_joined', 'last_login', 'is_staff', 'is_superuser')
    
    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]
    
    def get_permissions(self, obj):
        # Get permissions from groups
        group_permissions = set()
        for group in obj.groups.all():
            for permission in group.permissions.all():
                group_permissions.add(permission.codename)
        
        # Get direct user permissions
        user_permissions = set()
        for permission in obj.user_permissions.all():
            user_permissions.add(permission.codename)
        
        return list(group_permissions | user_permissions)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile - enhanced version of api_users EditUserSettingsView"""
    class Meta:
        model = UserModel
        fields = ('name', 'email', 'description', 'photo_url', 'first_name', 'last_name', 'timezone_difference')
        read_only_fields = ('email',)  # Email should not be changed via profile update
    
    def validate_name(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters long.')
        return value.strip()
    
    
    def validate_timezone_difference(self, value):
        if value < -12 or value > 14:
            raise serializers.ValidationError('Timezone difference must be between -12 and +14 hours.')
        return value


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users - not in api_users, useful for admin"""
    groups = serializers.SerializerMethodField()
    
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'email', 'is_active', 'date_joined', "groups", "name", "description", "photo_url", "user_type", "blocked")
        read_only_fields = ('id', 'date_joined', 'groups')
    
    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]
