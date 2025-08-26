from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, ServiceProviderProfile, ClientProfile, UserVerification, ServiceProviderService


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'is_verified', 'phone_display', 'location_display']
    list_filter = ['user_type', 'is_verified', 'gender', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone_number', 'address']
    ordering = ['-created_at']
    list_editable = ['is_verified']
    raw_id_fields = ['user', 'preferred_language']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_type', 'phone_number', 'address')
        }),
        ('Personal Details', {
            'fields': ('bio', 'date_of_birth', 'gender')
        }),
        ('Location', {
            'fields': ('city', 'state', 'country', 'postal_code')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'notification_preferences')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_date')
        }),
    )
    
    def phone_display(self, obj):
        return obj.phone_number if obj.phone_number else '-'
    phone_display.short_description = 'Phone'
    
    def location_display(self, obj):
        if obj.city and obj.state:
            return f"{obj.city}, {obj.state}"
        elif obj.city:
            return obj.city
        elif obj.state:
            return obj.state
        return '-'
    location_display.short_description = 'Location'


@admin.register(ServiceProviderProfile)
class ServiceProviderProfileAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'business_name', 'years_of_experience', 'is_available', 'is_verified_provider', 'average_rating', 'total_reviews']
    list_filter = ['is_verified_provider', 'is_available', 'created_at']
    search_fields = ['user_profile__user__first_name', 'user_profile__user__last_name', 'business_name']
    ordering = ['-average_rating', '-total_reviews']
    list_editable = ['is_verified_provider', 'is_available']
    raw_id_fields = ['user_profile']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_profile', 'business_name', 'business_description', 'years_of_experience')
        }),
        ('Business Details', {
            'fields': ('business_license', 'service_areas', 'travel_radius')
        }),
        ('Availability & Verification', {
            'fields': ('is_available', 'availability_schedule', 'is_verified_provider', 'verification_documents')
        }),
        ('Performance', {
            'fields': ('average_rating', 'total_reviews')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user_profile__user')


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'total_orders', 'completed_orders', 'cancelled_orders']
    list_filter = ['created_at']
    search_fields = ['user_profile__user__first_name', 'user_profile__user__last_name']
    ordering = ['-total_orders', '-created_at']
    raw_id_fields = ['user_profile', 'favorite_providers']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('user_profile',)
        }),
        ('Preferences', {
            'fields': ('preferred_service_areas', 'budget_preferences')
        }),
        ('Order History', {
            'fields': ('total_orders', 'completed_orders', 'cancelled_orders')
        }),
        ('Favorites', {
            'fields': ('favorite_providers',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user_profile__user')


@admin.register(ServiceProviderService)
class ServiceProviderServiceAdmin(admin.ModelAdmin):
    list_display = ['provider', 'subcategory', 'base_price', 'price_type', 'is_available']
    list_filter = ['price_type', 'is_available', 'created_at']
    search_fields = ['provider__user_profile__user__first_name', 'subcategory__name']
    ordering = ['-created_at']
    list_editable = ['is_available', 'base_price']
    raw_id_fields = ['provider', 'subcategory', 'available_addons']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('provider', 'subcategory', 'description')
        }),
        ('Pricing & Availability', {
            'fields': ('base_price', 'price_type', 'is_available', 'estimated_duration')
        }),
        ('Add-ons', {
            'fields': ('available_addons',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('provider__user_profile__user', 'subcategory')


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'verification_type', 'verification_status', 'verified_by', 'verified_at']
    list_filter = ['verification_type', 'verification_status', 'created_at']
    search_fields = ['user_profile__user__first_name', 'user_profile__user__last_name', 'verification_type']
    ordering = ['-created_at']
    list_editable = ['verification_status']
    raw_id_fields = ['user_profile', 'verified_by']
    
    fieldsets = (
        ('Verification Information', {
            'fields': ('user_profile', 'verification_type', 'verification_data')
        }),
        ('Status & Notes', {
            'fields': ('verification_status', 'admin_notes')
        }),
        ('Approval', {
            'fields': ('verified_by', 'verified_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user_profile__user', 'verified_by')
