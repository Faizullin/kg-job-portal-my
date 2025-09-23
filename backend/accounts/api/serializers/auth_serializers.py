from rest_framework import serializers
from ...models import UserModel


class FireBaseAuthSerializer(serializers.Serializer):
    """Serializer for Firebase authentication request"""
    id_token = serializers.CharField(help_text='Firebase ID token', required=True)


class FirebaseAuthResponseSerializer(serializers.Serializer):
    """Serializer for Firebase authentication response"""
    token = serializers.CharField(help_text='DRF authentication token')
    user = serializers.DictField(help_text='User information')
    message = serializers.CharField(help_text='Authentication success message')


class LogoutResponseSerializer(serializers.Serializer):
    """Serializer for logout response"""
    message = serializers.CharField(help_text='Logout confirmation message')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile display"""
    
    class Meta:
        model = UserModel
        fields = [
            'id', 'username', 'email', 'description', 'photo_url'
        ]
        read_only_fields = ['id', 'username']