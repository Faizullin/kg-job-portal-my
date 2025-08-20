from rest_framework import serializers
from ...models import UserModel


class FireBaseAuthSerializer(serializers.Serializer):
    """Serializer for Firebase authentication"""
    token = serializers.CharField(help_text='Firebase ID token')
