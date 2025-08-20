from rest_framework import serializers
























from ...models import UserModel


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information - enhanced version of api_users"""
    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserModel
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser',
            'groups', 'permissions', 'user_type', 'description', 'photo', 'photo_url',
            'timezone_difference', 'points', 'day_streak', 'max_day_streak'
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
    
    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        return obj.username


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile - enhanced version of api_users EditUserSettingsView"""
    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'description', 'timezone_difference')
    
    def validate_timezone_difference(self, value):
        if value < -12 or value > 14:
            raise serializers.ValidationError('Timezone difference must be between -12 and +14 hours.')
        return value


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users - not in api_users, useful for admin"""
    full_name = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'email', 'full_name', 'is_active', 'date_joined', 'groups')
    
    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username
    
    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]
