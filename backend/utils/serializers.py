from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AbstractTimestampedModelSerializer(serializers.ModelSerializer):
    """Serializer for models with timestamp fields."""

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True
        read_only_fields = ("created_at", "updated_at")
