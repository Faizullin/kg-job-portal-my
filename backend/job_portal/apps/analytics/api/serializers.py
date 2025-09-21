from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from utils.serializers import (
    AbstractTimestampedModelSerializer,
    AbstractChoiceFieldSerializerMixin,
)
from ..models import UserActivity, OrderAnalytics, ServiceCategoryAnalytics, PerformanceMetrics, BusinessMetrics


class UserActivitySerializer(AbstractTimestampedModelSerializer, AbstractChoiceFieldSerializerMixin):
    activity_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'activity_type', 'activity_type_display', 'context_data',
            'ip_address', 'user_agent', 'session_id', 'related_object_type', 
            'related_object_id', 'response_time', 'created_at'
        ]
    
    @extend_schema_field(serializers.CharField())
    def get_activity_type_display(self, obj):
        return self.get_choice_display(obj, 'activity_type')


class ServiceCategoryAnalyticsSerializer(AbstractTimestampedModelSerializer):
    
    class Meta:
        model = ServiceCategoryAnalytics
        fields = [
            'id', 'date', 'category', 'order_count', 'total_revenue',
            'average_order_value', 'bid_count', 'completion_rate', 'created_at'
        ]


class OrderAnalyticsSerializer(AbstractTimestampedModelSerializer):
    revenue_per_order = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderAnalytics
        fields = [
            'id', 'date', 'total_orders', 'new_orders', 'completed_orders',
            'cancelled_orders', 'average_order_value', 'revenue_per_order', 
            'total_revenue', 'total_bids', 'average_bids_per_order',
            'active_clients', 'active_providers', 'new_users', 'created_at'
        ]
    
    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_revenue_per_order(self, obj):
        if obj.total_orders and obj.total_orders > 0:
            return obj.total_revenue / obj.total_orders
        return 0


class PerformanceMetricsSerializer(AbstractTimestampedModelSerializer):
    
    class Meta:
        model = PerformanceMetrics
        fields = [
            'id', 'date', 'time_period', 'average_response_time', 'max_response_time',
            'min_response_time', 'total_errors', 'error_rate', 'active_users',
            'concurrent_users', 'database_queries', 'cpu_usage', 'memory_usage',
            'disk_usage', 'created_at'
        ]


class BusinessMetricsSerializer(AbstractTimestampedModelSerializer):
    
    class Meta:
        model = BusinessMetrics
        fields = [
            'id', 'date', 'gross_merchandise_volume', 'net_revenue', 'profit_margin',
            'order_fulfillment_rate', 'average_order_processing_time', 'customer_satisfaction_score',
            'month_over_month_growth', 'year_over_year_growth', 'market_share', 'competitive_position',
            'created_at'
        ]


class UserActivityCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['activity_type', 'context_data', 'related_object_type', 'related_object_id']


class ServiceCategoryAnalyticsCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = ServiceCategoryAnalytics
        fields = [
            'date', 'category', 'order_count', 'total_revenue',
            'average_order_value', 'bid_count', 'completion_rate'
        ]


class OrderAnalyticsCreateSerializer(AbstractTimestampedModelSerializer):
    class Meta:
        model = OrderAnalytics
        fields = [
            'date', 'total_orders', 'new_orders', 'completed_orders',
            'cancelled_orders', 'average_order_value', 'total_revenue',
            'total_bids', 'average_bids_per_order', 'active_clients', 'active_providers', 'new_users'
        ]
        

class DashboardResponseSerializer(serializers.Serializer):
    """Serializer for dashboard API response."""
    current_month = serializers.DictField()
    
    class Meta:
        fields = ['current_month']