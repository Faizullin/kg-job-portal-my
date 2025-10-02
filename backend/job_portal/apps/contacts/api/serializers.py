from rest_framework import serializers

from utils.serializers import AbstractTimestampedModelSerializer
from ..models import SimpleContact


class SimpleContactSerializer(AbstractTimestampedModelSerializer):
    """Minimal contact serializer for submissions."""

    class Meta:
        model = SimpleContact
        fields = [
            "id", "first_name", "last_name", "email", "user",
            "subject", "message", "phone", "enquiry_type",
            "ip_address", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "ip_address", "created_at", "updated_at"]
        extra_kwargs = {
            'email': {'required': True},
            'message': {'required': True},
            'phone': {'required': True},
            'enquiry_type': {'required': True}
        }
