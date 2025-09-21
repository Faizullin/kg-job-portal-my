from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from utils.serializers import (
    AbstractTimestampedModelSerializer, 
    AbstractSoftDeleteModelSerializer,
    AbstractChoiceFieldSerializerMixin,
    AbstractComputedFieldSerializerMixin
)
from ..models import Language, ServiceCategory, ServiceSubcategory, ServiceArea, SystemSettings, AppVersion, SupportFAQ


class LanguageSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    class Meta:
        model = Language
        fields = ['id', 'code', 'name', 'native_name', 'is_active', 'is_default', 'flag_icon', 'rtl_support']


class ServiceSubcategorySerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    complexity_level_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceSubcategory
        fields = ['id', 'name', 'description', 'icon', 'is_active', 'sort_order', 'image', 'featured', 'base_price', 'complexity_level', 'complexity_level_display']
    
    @extend_schema_field(serializers.CharField())
    def get_complexity_level_display(self, obj):
        return self.get_choice_display(obj, 'complexity_level')


class ServiceCategorySerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    subcategories = ServiceSubcategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'icon', 'color', 'is_active', 'sort_order', 'banner_image', 'featured', 'commission_rate', 'slug', 'subcategories']


class ServiceAreaSerializer(AbstractTimestampedModelSerializer):
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceArea
        fields = ['id', 'name', 'city', 'state', 'country', 'latitude', 'longitude', 'is_active', 'base_price_multiplier', 'travel_fee', 'coordinates']
    
    @extend_schema_field(serializers.CharField())
    def get_coordinates(self, obj):
        if obj.latitude and obj.longitude:
            return f"{obj.latitude:.4f}, {obj.longitude:.4f}"
        return None


class SystemSettingsSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    setting_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemSettings
        fields = ['id', 'key', 'value', 'description', 'is_public', 'setting_type', 'category', 'setting_type_display']
    
    @extend_schema_field(serializers.CharField())
    def get_setting_type_display(self, obj):
        return self.get_choice_display(obj, 'setting_type')


class AppVersionSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    platform_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AppVersion
        fields = ['id', 'version', 'build_number', 'platform', 'is_active', 'is_forced_update', 'release_date', 'download_url', 'platform_display']
    
    @extend_schema_field(serializers.CharField())
    def get_platform_display(self, obj):
        return self.get_choice_display(obj, 'platform')


class SupportFAQSerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    """Serializer for support FAQ items."""
    category_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportFAQ
        fields = ['id', 'question', 'answer', 'category', 'category_display', 'sort_order', 'is_popular', 'is_active', 'view_count', 'created_at']
    
    @extend_schema_field(serializers.CharField())
    def get_category_display(self, obj):
        return self.get_choice_display(obj, 'category')
