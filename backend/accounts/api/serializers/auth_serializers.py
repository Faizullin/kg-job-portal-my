from rest_framework import serializers
from ...models import UserModel


class FireBaseAuthSerializer(serializers.Serializer):
    """Serializer for Firebase authentication request"""
    firebase_user_id = serializers.CharField(help_text='Firebase user ID', required=True)


class FirebaseAuthResponseSerializer(serializers.Serializer):
    """Serializer for Firebase authentication response"""
    token = serializers.CharField(help_text='DRF authentication token')
    user = serializers.DictField(help_text='User information')
    message = serializers.CharField(help_text='Authentication success message')


class LogoutResponseSerializer(serializers.Serializer):
    """Serializer for logout response"""
    message = serializers.CharField(help_text='Logout confirmation message')