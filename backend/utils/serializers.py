from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AbstractTimestampedSerializerMixin(serializers.Serializer):
    """Mixin to add timestamp fields to serializers."""

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class AbstractTimestampedModelSerializer(AbstractTimestampedSerializerMixin, serializers.ModelSerializer):
    """Serializer for models with timestamp fields."""

    class Meta:
        abstract = True
        read_only_fields = ('created_at', 'updated_at')


class AbstractChoiceFieldSerializerMixin:
    """Mixin to handle choice fields with human-readable labels."""

    def get_choice_display(self, obj, field_name):
        """Get human-readable choice value."""
        field = obj._meta.get_field(field_name)
        if hasattr(field, 'choices') and field.choices:
            value = getattr(obj, field_name)
            return dict(field.choices).get(value, value)
        return getattr(obj, field_name)
