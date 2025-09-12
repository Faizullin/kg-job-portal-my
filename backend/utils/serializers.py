from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AbstractTimestampedSerializerMixin(serializers.Serializer):
    """Mixin to add timestamp fields to serializers."""

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class AbstractSoftDeleteSerializerMixin(serializers.Serializer):
    """Mixin to add soft delete fields to serializers."""

    deleted_at = serializers.DateTimeField(read_only=True)
    restored_at = serializers.DateTimeField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)


class AbstractMetaSerializerMixin(serializers.Serializer):
    """Mixin to add meta fields to serializers."""

    meta_title = serializers.CharField(max_length=80, required=False, allow_blank=True)
    meta_keywords = serializers.CharField(max_length=255, required=False, allow_blank=True)
    meta_description = serializers.CharField(required=False, allow_blank=True)
    use_ssr = serializers.BooleanField(default=False)
    render_url = serializers.CharField(max_length=80, required=False, allow_blank=True)


class AbstractTimestampedModelSerializer(AbstractTimestampedSerializerMixin, serializers.ModelSerializer):
    """Serializer for models with timestamp fields."""

    class Meta:
        abstract = True


class AbstractSoftDeleteModelSerializer(AbstractSoftDeleteSerializerMixin, serializers.ModelSerializer):
    """Serializer for models with soft delete functionality."""

    class Meta:
        abstract = True


class AbstractMetaModelSerializer(AbstractMetaSerializerMixin, serializers.ModelSerializer):
    """Serializer for models with meta fields."""

    class Meta:
        abstract = True


class AbstractFullModelSerializer(
    AbstractTimestampedSerializerMixin,
    AbstractSoftDeleteSerializerMixin,
    AbstractMetaSerializerMixin,
    serializers.ModelSerializer
):
    """Complete serializer with all common fields."""

    class Meta:
        abstract = True


class AbstractNestedSerializerMixin:
    """Mixin to handle nested serialization."""

    def get_nested_data(self, obj, field_name, serializer_class):
        """Get nested serialized data for a field."""
        related_obj = getattr(obj, field_name, None)
        if related_obj:
            return serializer_class(related_obj, context=self.context).data
        return None


class AbstractChoiceFieldSerializerMixin:
    """Mixin to handle choice fields with human-readable labels."""

    def get_choice_display(self, obj, field_name):
        """Get human-readable choice value."""
        field = obj._meta.get_field(field_name)
        if hasattr(field, 'choices') and field.choices:
            value = getattr(obj, field_name)
            return dict(field.choices).get(value, value)
        return getattr(obj, field_name)


class AbstractComputedFieldSerializerMixin:
    """Mixin to add computed fields to serializers."""

    def get_computed_field(self, obj, field_name, computation_func):
        """Get computed field value."""
        return computation_func(obj)
