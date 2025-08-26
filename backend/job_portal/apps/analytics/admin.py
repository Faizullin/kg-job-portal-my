from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Avg
from .models import UserActivity, OrderAnalytics, ServiceCategoryAnalytics, UserRetentionAnalytics, SearchAnalytics, PerformanceMetrics, BusinessMetrics


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'activity_type', 'description_preview', 'ip_address',
        'created_at'
    ]
    list_filter = ['activity_type', 'created_at']
    search_fields = ['description', 'user__first_name', 'user__last_name', 'ip_address']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'activity_type', 'description')
        }),
        ('Metadata', {
            'fields': ('metadata', 'ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def description_preview(self, obj):
        if obj.description:
            return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
        return '-'
    description_preview.short_description = 'Description'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ServiceCategoryAnalytics)
class ServiceCategoryAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'service_category', 'period_start', 'period_end', 'total_orders',
        'total_revenue', 'average_rating', 'completion_rate', 'customer_satisfaction'
    ]
    list_filter = ['service_category', 'period_start', 'period_end']
    search_fields = ['service_category__name']
    ordering = ['-period_start']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service_category', 'period_start', 'period_end')
        }),
        ('Metrics', {
            'fields': ('total_orders', 'total_revenue', 'average_rating')
        }),
        ('Performance', {
            'fields': ('completion_rate', 'customer_satisfaction')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('service_category')


@admin.register(OrderAnalytics)
class OrderAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'period_start', 'period_end', 'total_orders', 'completed_orders',
        'cancelled_orders', 'status', 'average_order_value', 'total_revenue'
    ]
    list_filter = ['status', 'period_start', 'period_end']
    ordering = ['-period_start']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_start', 'period_end', 'status')
        }),
        ('Order Metrics', {
            'fields': ('total_orders', 'completed_orders', 'cancelled_orders')
        }),
        ('Financial Metrics', {
            'fields': ('average_order_value', 'total_revenue')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(UserRetentionAnalytics)
class UserRetentionAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'period_start', 'period_end', 'total_users', 'new_users',
        'returning_users', 'churn_rate'
    ]
    list_filter = ['period_start', 'period_end']
    ordering = ['-period_start']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_start', 'period_end')
        }),
        ('User Metrics', {
            'fields': ('total_users', 'new_users', 'returning_users')
        }),
        ('Churn Rate', {
            'fields': ('churn_rate',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'period_start', 'period_end', 'total_searches', 'unique_searches',
        'average_search_depth', 'conversion_rate'
    ]
    list_filter = ['period_start', 'period_end']
    ordering = ['-period_start']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_start', 'period_end')
        }),
        ('Search Metrics', {
            'fields': ('total_searches', 'unique_searches')
        }),
        ('Conversion Rate', {
            'fields': ('average_search_depth', 'conversion_rate')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(PerformanceMetrics)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'period_start', 'period_end', 'total_requests', 'successful_requests',
        'failed_requests', 'average_response_time', 'error_rate'
    ]
    list_filter = ['period_start', 'period_end']
    ordering = ['-period_start']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_start', 'period_end')
        }),
        ('Performance Metrics', {
            'fields': ('total_requests', 'successful_requests', 'failed_requests')
        }),
        ('Error Rate', {
            'fields': ('average_response_time', 'error_rate')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(BusinessMetrics)
class BusinessMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'period_start', 'period_end', 'gross_revenue', 'net_revenue',
        'commission_revenue', 'tax_amount', 'refund_amount', 'profit_margin_display'
    ]
    list_filter = ['period_start', 'period_end']
    ordering = ['-period_start']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_start', 'period_end')
        }),
        ('Revenue Breakdown', {
            'fields': ('gross_revenue', 'commission_revenue', 'tax_amount')
        }),
        ('Net Revenue', {
            'fields': ('net_revenue', 'refund_amount')
        }),
    )
    
    def profit_margin_display(self, obj):
        if obj.gross_revenue and obj.gross_revenue > 0:
            margin = ((obj.net_revenue / obj.gross_revenue) * 100)
            return f"{margin:.1f}%"
        return '-'
    profit_margin_display.short_description = 'Profit Margin'
    
    def get_queryset(self, request):
        return super().get_queryset(request)
