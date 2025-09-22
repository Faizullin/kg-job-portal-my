from django.contrib import admin
from .models import UserProfile, ServiceProviderProfile, ClientProfile


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
    list_display = ['user_profile', 'business_name', 'is_available', 'is_verified_provider', 'average_rating', 'total_reviews']
    list_filter = ['is_verified_provider', 'is_available', 'created_at']
    search_fields = ['user_profile__user__first_name', 'user_profile__user__last_name', 'business_name']
    ordering = ['-average_rating', '-total_reviews']
    list_editable = ['is_verified_provider', 'is_available']
    raw_id_fields = ['user_profile']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_profile', 'business_name', 'business_description')
        }),
        ('Business Details', {
            'fields': ('service_areas', 'services_offered', 'works_remotely', 'accepts_clients_at_location', 'travels_to_clients')
        }),
        ('Availability & Verification', {
            'fields': ('is_available', 'is_verified_provider')
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
            'fields': ('preferred_services',)
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


