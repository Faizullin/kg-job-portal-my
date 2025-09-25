from django.contrib import admin
from .models import UserProfile, ServiceProviderProfile, ClientProfile, ProviderStatistics


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'phone_display', 'location_display']
    list_filter = ['is_verified', 'gender', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone_number', 'address']
    ordering = ['-created_at']
    list_editable = ['is_verified']
    raw_id_fields = ['user', 'preferred_language']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'address')
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
    list_display = ['user_profile', 'business_name', 'is_available', 'is_verified_provider', 'get_average_rating', 'get_total_reviews']
    list_filter = ['is_verified_provider', 'is_available', 'created_at']
    search_fields = ['user_profile__user__first_name', 'user_profile__user__last_name', 'business_name']
    ordering = ['-created_at']
    list_editable = ['is_verified_provider', 'is_available']
    raw_id_fields = ['user_profile', 'profession']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_profile', 'business_name', 'business_description', 'profession')
        }),
        ('Business Details', {
            'fields': ('service_areas', 'services_offered', 'works_remotely', 'accepts_clients_at_location', 'travels_to_clients')
        }),
        ('Pricing & Availability', {
            'fields': ('hourly_rate', 'is_available', 'response_time_hours')
        }),
        ('Professional Information', {
            'fields': ('work_experience_start_year', 'education_institution', 'education_years', 'languages', 'about_description')
        }),
        ('Location & Status', {
            'fields': ('current_location', 'is_online', 'last_seen')
        }),
        ('Verification', {
            'fields': ('is_verified_provider', 'is_top_master')
        }),
    )
    
    def get_average_rating(self, obj):
        if hasattr(obj, 'statistics') and obj.statistics:
            return obj.statistics.average_rating
        return "0.00"
    get_average_rating.short_description = 'Avg Rating'
    
    def get_total_reviews(self, obj):
        if hasattr(obj, 'statistics') and obj.statistics:
            return obj.statistics.total_reviews
        return 0
    get_total_reviews.short_description = 'Total Reviews'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user_profile__user', 'statistics')


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


@admin.register(ProviderStatistics)
class ProviderStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'provider', 'total_jobs_completed', 'average_rating', 'total_reviews',
        'on_time_percentage', 'repeat_customer_percentage', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['provider__user_profile__user__first_name', 'provider__user_profile__user__last_name']
    ordering = ['-average_rating', '-total_reviews']
    raw_id_fields = ['provider']
    
    fieldsets = (
        ('Provider Information', {
            'fields': ('provider',)
        }),
        ('Performance Metrics', {
            'fields': ('total_jobs_completed', 'on_time_percentage', 'repeat_customer_percentage')
        }),
        ('Ratings & Reviews', {
            'fields': ('average_rating', 'total_reviews')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('provider__user_profile__user')


