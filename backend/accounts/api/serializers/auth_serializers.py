from django.contrib.auth import get_user_model
from rest_framework import serializers

UserModel = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile display"""

    groups = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = UserModel
        fields = [
            'id', 'username', 'email', 'description', 'photo_url', "groups",
        ]
        read_only_fields = ['id', 'username']


class FireBaseAuthSerializer(serializers.Serializer):
    """Serializer for Firebase authentication request"""

    id_token = serializers.CharField(help_text='Firebase ID token', required=True)


class FirebaseAuthResponseSerializer(serializers.Serializer):
    """Serializer for Firebase authentication response"""

    token = serializers.CharField(help_text='DRF authentication token')
    user = UserProfileSerializer(read_only=True)
    message = serializers.CharField()


class LogoutResponseSerializer(serializers.Serializer):
    """Serializer for logout response"""

    message = serializers.CharField(help_text='Logout confirmation message')
