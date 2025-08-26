from django.contrib import admin
from django.utils.html import format_html
from .models import Language, ServiceCategory, ServiceSubcategory, ServiceArea, SystemSettings, AppVersion


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'native_name', 'is_active', 'is_default', 'rtl_support', 'flag_icon_display']
    list_filter = ['is_active', 'is_default', 'rtl_support']
    search_fields = ['code', 'name', 'native_name']
    ordering = ['name']
    list_editable = ['is_active', 'is_default']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'native_name', 'is_active', 'is_default')
        }),
        ('Advanced Features', {
            'fields': ('flag_icon', 'rtl_support', 'locale_code', 'currency_code'),
            'classes': ('collapse',)
        }),
    )
    
    def flag_icon_display(self, obj):
        if obj.flag_icon:
            return format_html('<span style="font-size: 20px;">{}</span>', obj.flag_icon)
        return '-'
    flag_icon_display.short_description = 'Flag'


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'featured', 'sort_order', 'commission_rate', 'slug', 'requirements_display']
    list_filter = ['is_active', 'featured', 'requires_license', 'requires_insurance', 'requires_background_check']
    search_fields = ['name', 'description', 'slug']
    ordering = ['sort_order', 'name']
    list_editable = ['is_active', 'featured', 'sort_order', 'commission_rate']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'icon', 'color', 'is_active', 'sort_order')
        }),
        ('Features & Pricing', {
            'fields': ('banner_image', 'featured', 'commission_rate', 'min_price', 'max_price')
        }),
        ('Duration & Requirements', {
            'fields': ('estimated_duration_min', 'estimated_duration_max', 'requires_license', 
                      'requires_insurance', 'requires_background_check'),
            'classes': ('collapse',)
        }),
        ('SEO & Marketing', {
            'fields': ('meta_title', 'meta_description', 'keywords', 'slug'),
            'classes': ('collapse',)
        }),
    )
    
    def requirements_display(self, obj):
        reqs = []
        if obj.requires_license:
            reqs.append('License')
        if obj.requires_insurance:
            reqs.append('Insurance')
        if obj.requires_background_check:
            reqs.append('Background Check')
        return ', '.join(reqs) if reqs else 'None'
    requirements_display.short_description = 'Requirements'


@admin.register(ServiceSubcategory)
class ServiceSubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'featured', 'sort_order', 'complexity_level', 'base_price', 'duration_display']
    list_filter = ['is_active', 'featured', 'complexity_level', 'category']
    search_fields = ['name', 'description']
    ordering = ['category', 'sort_order', 'name']
    list_editable = ['is_active', 'featured', 'sort_order', 'base_price']
    raw_id_fields = ['category']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'description', 'icon', 'is_active', 'sort_order')
        }),
        ('Features & Pricing', {
            'fields': ('image', 'featured', 'base_price', 'price_range_min', 'price_range_max')
        }),
        ('Service Details', {
            'fields': ('estimated_duration', 'complexity_level', 'required_tools', 'required_materials'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        if obj.estimated_duration:
            return f"{obj.estimated_duration} hours"
        return '-'
    duration_display.short_description = 'Duration'


@admin.register(ServiceArea)
class ServiceAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'country', 'is_active', 'base_price_multiplier', 'travel_fee', 'coordinates_display']
    list_filter = ['is_active', 'country', 'state']
    search_fields = ['name', 'city', 'state', 'country']
    ordering = ['country', 'state', 'city', 'name']
    list_editable = ['is_active', 'base_price_multiplier', 'travel_fee']
    
    fieldsets = (
        ('Location Information', {
            'fields': ('name', 'city', 'state', 'country')
        }),
        ('Geographic Data', {
            'fields': ('latitude', 'longitude', 'postal_codes'),
            'classes': ('collapse',)
        }),
        ('Service Configuration', {
            'fields': ('is_active', 'service_categories', 'base_price_multiplier', 'travel_fee')
        }),
    )
    
    filter_horizontal = ['service_categories']
    
    def coordinates_display(self, obj):
        if obj.latitude and obj.longitude:
            return format_html('{:.4f}, {:.4f}', obj.latitude, obj.longitude)
        return '-'
    coordinates_display.short_description = 'Coordinates'


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'setting_type', 'is_public', 'requires_admin', 'category', 'value_preview']
    list_filter = ['setting_type', 'is_public', 'requires_admin', 'category']
    search_fields = ['key', 'description']
    ordering = ['category', 'key']
    list_editable = ['is_public', 'requires_admin']
    
    fieldsets = (
        ('Basic Settings', {
            'fields': ('key', 'value', 'description', 'setting_type', 'is_public')
        }),
        ('Access Control', {
            'fields': ('requires_admin', 'category'),
            'classes': ('collapse',)
        }),
        ('Validation', {
            'fields': ('validation_regex', 'min_value', 'max_value'),
            'classes': ('collapse',)
        }),
    )
    
    def value_preview(self, obj):
        if len(str(obj.value)) > 50:
            return format_html('{}...', str(obj.value)[:50])
        return obj.value
    value_preview.short_description = 'Value Preview'


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ['version', 'build_number', 'platform', 'is_active', 'is_forced_update', 'release_date', 'file_size_display']
    list_filter = ['is_active', 'is_forced_update', 'platform']
    search_fields = ['version', 'release_notes']
    ordering = ['-build_number']
    list_editable = ['is_active', 'is_forced_update']
    
    fieldsets = (
        ('Version Information', {
            'fields': ('version', 'build_number', 'platform', 'is_active', 'is_forced_update')
        }),
        ('Release Details', {
            'fields': ('release_notes', 'release_date', 'download_url', 'file_size', 'checksum')
        }),
        ('Compatibility', {
            'fields': ('min_os_version', 'max_os_version', 'device_requirements'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['release_date']
    
    def file_size_display(self, obj):
        if obj.file_size:
            size_kb = obj.file_size / 1024
            if size_kb > 1024:
                return f"{size_kb/1024:.1f} MB"
            return f"{size_kb:.0f} KB"
        return '-'
    file_size_display.short_description = 'File Size'
