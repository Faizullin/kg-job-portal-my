from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Avg
from .models import UserActivity, OrderAnalytics, ServiceCategoryAnalytics, UserRetentionAnalytics, SearchAnalytics, PerformanceMetrics, BusinessMetrics


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'activity_type', 'context_data_preview', 'ip_address',
        'created_at'
    ]
    list_filter = ['activity_type', 'created_at']
    search_fields = ['context_data', 'user__first_name', 'user__last_name', 'ip_address']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'activity_type', 'context_data')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'session_id', 'related_object_type', 'related_object_id')
        }),
        ('Performance', {
            'fields': ('response_time',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def context_data_preview(self, obj):
        if obj.context_data:
            return str(obj.context_data)[:100] + '...' if len(str(obj.context_data)) > 100 else str(obj.context_data)
        return '-'
    context_data_preview.short_description = 'Context Data'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ServiceCategoryAnalytics)
class ServiceCategoryAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'category', 'date', 'order_count', 'total_revenue',
        'average_order_value', 'bid_count', 'completion_rate'
    ]
    list_filter = ['category', 'date']
    search_fields = ['category__name']
    ordering = ['-date']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('category', 'date')
        }),
        ('Metrics', {
            'fields': ('order_count', 'total_revenue', 'average_order_value')
        }),
        ('Performance', {
            'fields': ('bid_count', 'completion_rate')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(OrderAnalytics)
class OrderAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'date', 'total_orders', 'completed_orders',
        'cancelled_orders', 'average_order_value', 'total_revenue'
    ]
    list_filter = ['date']
    ordering = ['-date']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('date',)
        }),
        ('Order Metrics', {
            'fields': ('total_orders', 'new_orders', 'completed_orders', 'cancelled_orders')
        }),
        ('Financial Metrics', {
            'fields': ('average_order_value', 'total_revenue', 'total_fees')
        }),
        ('Service Metrics', {
            'fields': ('total_bids', 'average_bids_per_order')
        }),
        ('User Metrics', {
            'fields': ('active_clients', 'active_providers', 'new_users')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(UserRetentionAnalytics)
class UserRetentionAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'date', 'user_type', 'cohort_size', 'day_1_retention',
        'day_7_retention', 'day_30_retention'
    ]
    list_filter = ['date', 'user_type']
    ordering = ['-date']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('date', 'user_type')
        }),
        ('Cohort Metrics', {
            'fields': ('cohort_size', 'day_1_retention', 'day_7_retention', 'day_30_retention')
        }),
        ('Engagement Metrics', {
            'fields': ('average_sessions_per_user', 'average_session_duration')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'date', 'total_searches', 'unique_searchers',
        'searches_with_results', 'search_to_order_conversion_rate'
    ]
    list_filter = ['date']
    ordering = ['-date']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('date',)
        }),
        ('Search Metrics', {
            'fields': ('total_searches', 'unique_searchers', 'searches_with_results', 'searches_without_results')
        }),
        ('Popular Terms', {
            'fields': ('top_search_terms', 'top_categories_searched')
        }),
        ('Conversion Metrics', {
            'fields': ('searches_leading_to_orders', 'search_to_order_conversion_rate')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(PerformanceMetrics)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'date', 'time_period', 'average_response_time', 'error_rate',
        'active_users', 'cpu_usage', 'memory_usage'
    ]
    list_filter = ['date', 'time_period']
    ordering = ['-date']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('date', 'time_period')
        }),
        ('Performance Metrics', {
            'fields': ('average_response_time', 'max_response_time', 'min_response_time')
        }),
        ('Error Metrics', {
            'fields': ('total_errors', 'error_rate')
        }),
        ('System Metrics', {
            'fields': ('active_users', 'concurrent_users', 'database_queries')
        }),
        ('Infrastructure', {
            'fields': ('cpu_usage', 'memory_usage', 'disk_usage')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(BusinessMetrics)
class BusinessMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'date', 'gross_merchandise_volume', 'net_revenue',
        'profit_margin', 'order_fulfillment_rate', 'customer_satisfaction_score'
    ]
    list_filter = ['date', 'competitive_position']
    ordering = ['-date']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('date',)
        }),
        ('Financial KPIs', {
            'fields': ('gross_merchandise_volume', 'net_revenue', 'profit_margin')
        }),
        ('Operational KPIs', {
            'fields': ('order_fulfillment_rate', 'average_order_processing_time', 'customer_satisfaction_score')
        }),
        ('Growth Metrics', {
            'fields': ('month_over_month_growth', 'year_over_year_growth')
        }),
        ('Market Metrics', {
            'fields': ('market_share', 'competitive_position')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)
