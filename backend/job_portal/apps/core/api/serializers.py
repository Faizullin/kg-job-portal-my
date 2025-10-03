from rest_framework import serializers

from utils.serializers import (
    AbstractTimestampedModelSerializer,
)
from ..models import (
    AppVersion,
    Language,
    ServiceArea,
    ServiceCategory,
    ServiceSubcategory,
    SupportFAQ,
    SystemSettings,
)


class LanguageSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = Language
        fields = [
            "id",
            "code",
            "name",
            "native_name",
            "is_active",
            "is_default",
            "flag_icon",
            "rtl_support",
        ]


class ServiceSubcategorySerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceSubcategory
        fields = [
            "id",
            "name",
            "description",
            "icon",
            "is_active",
            "sort_order",
            "image",
            "featured",
            "base_price",
            "complexity_level",
        ]


class ServiceCategorySerializer(AbstractTimestampedModelSerializer):
    subcategories = ServiceSubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = [
            "id",
            "name",
            "description",
            "icon",
            "color",
            "is_active",
            "sort_order",
            "banner_image",
            "featured",
            "commission_rate",
            "slug",
            "subcategories",
        ]


class ServiceAreaSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceArea
        fields = [
            "id",
            "name",
            "city",
            "state",
            "country",
            "latitude",
            "longitude",
            "is_active",
            "base_price_multiplier",
            "travel_fee",
            "service_categories",
        ]


class SystemSettingsSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = SystemSettings
        fields = [
            "id",
            "key",
            "value",
            "description",
            "is_public",
            "is_active",
            "setting_type",
        ]


class SupportFAQSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = SupportFAQ
        fields = [
            "id",
            "question",
            "answer",
            "category",
            "language",
            "sort_order",
            "is_popular",
            "is_active",
            "view_count",
            "created_at",
        ]


# CRUD Serializers for Create/Update operations
class ServiceCategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating service categories."""

    class Meta:
        model = ServiceCategory
        fields = [
            "name",
            "description",
            "icon",
            "color",
            "is_active",
            "sort_order",
            "banner_image",
            "featured",
            "commission_rate",
            "min_price",
            "max_price",
            "estimated_duration_min",
            "estimated_duration_max",
            "meta_title",
            "meta_description",
            "keywords",
            "slug",
            "requires_license",
            "requires_insurance",
            "requires_background_check",
        ]
        extra_kwargs = {
            "slug": {"required": False},  # Auto-generated if not provided
        }


class ServiceSubcategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating service subcategories."""

    class Meta:
        model = ServiceSubcategory
        fields = [
            "id",
            "category",
            "name",
            "description",
            "icon",
            "is_active",
            "sort_order",
            "image",
            "featured",
            "base_price",
            "price_range_min",
            "price_range_max",
            "estimated_duration",
            "complexity_level",
            "safety_requirements",
            "slug",
            "meta_title",
            "meta_description",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "slug": {"required": False},  # Auto-generated if not provided
        }


class ServiceAreaCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating service areas."""

    class Meta:
        model = ServiceArea
        fields = [
            "name",
            "city",
            "state",
            "country",
            "latitude",
            "longitude",
            "postal_codes",
            "is_active",
            "service_categories",
            "base_price_multiplier",
            "travel_fee",
        ]


class SystemSettingsCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating system settings."""

    class Meta:
        model = SystemSettings
        fields = [
            "key",
            "value",
            "description",
            "is_public",
            "setting_type",
            "validation_regex",
            "min_value",
            "max_value",
            "requires_admin",
            "category",
        ]


class AppVersionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating app versions."""

    class Meta:
        model = AppVersion
        fields = [
            "version",
            "build_number",
            "release_notes",
            "is_forced_update",
            "is_active",
            "platform",
            "download_url",
            "file_size",
            "checksum",
            "min_os_version",
            "max_os_version",
            "device_requirements",
        ]


class SupportFAQCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating support FAQ items."""

    class Meta:
        model = SupportFAQ
        fields = [
            "question",
            "answer",
            "category",
            "sort_order",
            "is_popular",
            "is_active",
        ]
