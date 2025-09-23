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
            'groups', 'permissions', 'description', 
            'photo', 'photo_url'
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
        fields = ('email', 'description', 'photo_url', 'first_name', 'last_name')
        read_only_fields = ('email',)  # Email should not be changed via profile update
    



class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users - not in api_users, useful for admin"""
    groups = serializers.SerializerMethodField()
    
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'email', 'is_active', 'date_joined', "groups", "description", "photo_url", "user_type", "blocked")
        read_only_fields = ('id', 'date_joined', 'groups')
    
    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]
