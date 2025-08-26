from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.contrib.auth import get_user_model
from django.utils import timezone
from typing import Any, Dict, List, Optional

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


class AbstractUserSerializerMixin(serializers.Serializer):
    """Mixin to add user-related fields to serializers."""
    
    created_by = serializers.PrimaryKeyRelatedField(
        required=False,
        read_only=True
    ) 
    updated_by = serializers.PrimaryKeyRelatedField(
        required=False,
        read_only=True
    )


class AbstractBaseModelSerializer(serializers.ModelSerializer):
    """Base serializer for all models."""
    
    class Meta:
        abstract = True
    
    def create(self, validated_data):
        """Override create to set user fields if available."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if 'created_by' not in validated_data:
                validated_data['created_by'] = request.user
            if 'updated_by' not in validated_data:
                validated_data['updated_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Override update to set updated_by field if available."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class AbstractTimestampedModelSerializer(AbstractTimestampedSerializerMixin, AbstractBaseModelSerializer):
    """Serializer for models with timestamp fields."""
    
    class Meta(AbstractBaseModelSerializer.Meta):
        abstract = True


class AbstractSoftDeleteModelSerializer(AbstractSoftDeleteSerializerMixin, AbstractBaseModelSerializer):
    """Serializer for models with soft delete functionality."""
    
    class Meta(AbstractBaseModelSerializer.Meta):
        abstract = True


class AbstractMetaModelSerializer(AbstractMetaSerializerMixin, AbstractBaseModelSerializer):
    """Serializer for models with meta fields."""
    
    class Meta(AbstractBaseModelSerializer.Meta):
        abstract = True


class AbstractAuditModelSerializer(AbstractUserSerializerMixin, AbstractTimestampedModelSerializer):
    """Serializer for models with audit trail functionality."""
    
    class Meta(AbstractTimestampedModelSerializer.Meta):
        abstract = True


class AbstractFullModelSerializer(
    AbstractTimestampedSerializerMixin,
    AbstractSoftDeleteSerializerMixin,
    AbstractMetaSerializerMixin,
    AbstractUserSerializerMixin,
    AbstractBaseModelSerializer
):
    """Complete serializer with all common fields."""
    
    class Meta(AbstractBaseModelSerializer.Meta):
        abstract = True


class AbstractNestedSerializerMixin:
    """Mixin to handle nested serialization."""
    
    def get_nested_data(self, obj, field_name, serializer_class):
        """Get nested serialized data for a field."""
        related_obj = getattr(obj, field_name, None)
        if related_obj:
            return serializer_class(related_obj, context=self.context).data
        return None


class AbstractDynamicFieldsSerializerMixin:
    """Mixin to dynamically include/exclude fields."""
    
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)
        
        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class AbstractValidationSerializerMixin:
    """Mixin to add custom validation methods."""
    
    def validate_unique_together(self, attrs, field_names):
        """Validate unique together constraint."""
        model = self.Meta.model
        if hasattr(model._meta, 'unique_together'):
            for unique_fields in model._meta.unique_together:
                if all(field in attrs for field in unique_fields):
                    filter_kwargs = {field: attrs[field] for field in unique_fields}
                    if self.instance:
                        filter_kwargs['pk__ne'] = self.instance.pk
                    
                    if model.objects.filter(**filter_kwargs).exists():
                        raise serializers.ValidationError(
                            f"Object with these {', '.join(unique_fields)} already exists."
                        )
        return attrs


class AbstractSlugSerializerMixin:
    """Mixin to handle slug generation."""
    
    def validate_slug(self, value):
        """Validate and generate slug if not provided."""
        if not value:
            # Generate slug from title or name field
            title = self.initial_data.get('title') or self.initial_data.get('name')
            if title:
                from utils.abstract_models import generate_slug
                value = generate_slug(title)
        
        return value


class AbstractFileUploadSerializerMixin:
    """Mixin to handle file uploads."""
    
    def validate_file(self, value):
        """Validate uploaded file."""
        if value:
            # Check file size (example: 10MB limit)
            max_size = 10 * 1024 * 1024  # 10MB
            if value.size > max_size:
                raise serializers.ValidationError(
                    f"File size must be no more than {max_size // (1024 * 1024)}MB."
                )
            
            # Check file type (example: images only)
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Only JPEG, PNG and GIF images are allowed."
                )
        
        return value


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


class AbstractRelatedFieldSerializerMixin:
    """Mixin to handle related field serialization."""
    
    def get_related_objects(self, obj, field_name, serializer_class):
        """Get serialized related objects."""
        related_objects = getattr(obj, field_name).all()
        return serializer_class(related_objects, many=True, context=self.context).data


class AbstractCacheSerializerMixin:
    """Mixin to add caching to serializers."""
    
    def to_representation(self, instance):
        """Override to add caching."""
        cache_key = f"serializer_{instance._meta.model.__name__}_{instance.pk}"
        
        # Try to get from cache
        from django.core.cache import cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Serialize and cache
        data = super().to_representation(instance)
        cache.set(cache_key, data, 300)  # Cache for 5 minutes
        
        return data
