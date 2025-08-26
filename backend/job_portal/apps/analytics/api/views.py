from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from utils.crud_base.views import AbstractBaseListApiView, AbstractBaseApiView
from utils.permissions import AbstractIsAuthenticatedOrReadOnly, AbstractHasSpecificPermission
from ..models import UserActivity, OrderAnalytics, ServiceCategoryAnalytics, PerformanceMetrics, BusinessMetrics
from .serializers import (
    UserActivitySerializer, OrderAnalyticsSerializer, ServiceCategoryAnalyticsSerializer,
    PerformanceMetricsSerializer, BusinessMetricsSerializer, UserActivityCreateSerializer,
    ServiceCategoryAnalyticsCreateSerializer, OrderAnalyticsCreateSerializer, 
    BusinessMetricsCreateSerializer, PerformanceMetricsCreateSerializer
)


class UserActivityApiView(AbstractBaseListApiView):
    serializer_class = UserActivitySerializer
    permission_classes = [AbstractHasSpecificPermission(['analytics.view_useractivity'])]
    filterset_fields = ['activity_type', 'user']
    search_fields = ['context_data', 'user__first_name']
    ordering_fields = ['activity_type', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return UserActivity.objects.filter(is_deleted=False).select_related('user')
    
    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """Get recent user activities (last 24 hours)."""
        yesterday = timezone.now() - timedelta(days=1)
        
        activities = UserActivity.objects.filter(
            created_at__gte=yesterday, is_deleted=False
        ).select_related('user')[:100]
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_summary(self, request):
        """Get activity summary for a specific user."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)
        
        activities = UserActivity.objects.filter(
            user_id=user_id, is_deleted=False
        ).select_related('user')
        
        # Group by activity type
        summary = {}
        for activity in activities:
            activity_type = activity.activity_type
            if activity_type not in summary:
                summary[activity_type] = 0
            summary[activity_type] += 1
        
        return Response({
            'user_id': user_id,
            'total_activities': activities.count(),
            'activity_breakdown': summary
        })


class UserActivityCreateApiView(generics.CreateAPIView):
    serializer_class = UserActivityCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class ServiceCategoryAnalyticsApiView(AbstractBaseListApiView):
    serializer_class = ServiceCategoryAnalyticsSerializer
    permission_classes = [AbstractHasSpecificPermission(['analytics.view_servicecategoryanalytics'])]
    filterset_fields = ['category', 'date']
    ordering_fields = ['date', 'total_revenue', 'order_count']
    ordering = ['-date']
    
    def get_queryset(self):
        return ServiceCategoryAnalytics.objects.filter(is_deleted=False).select_related('category')
    
    @action(detail=False, methods=['get'])
    def top_performing_categories(self, request):
        """Get top performing service categories by revenue."""
        categories = ServiceCategoryAnalytics.objects.filter(
            is_deleted=False
        ).select_related('category').order_by('-total_revenue')[:10]
        
        serializer = ServiceCategoryAnalyticsSerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def category_comparison(self, request):
        """Compare service categories performance."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({'error': 'start_date and end_date are required'}, status=400)
        
        metrics = ServiceCategoryAnalytics.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_deleted=False
        ).select_related('category')
        
        serializer = ServiceCategoryAnalyticsSerializer(metrics, many=True)
        return Response(serializer.data)


class ServiceCategoryAnalyticsCreateApiView(generics.CreateAPIView):
    serializer_class = ServiceCategoryAnalyticsCreateSerializer
    permission_classes = [AbstractHasSpecificPermission(['analytics.add_servicecategoryanalytics'])]


class OrderAnalyticsApiView(AbstractBaseListApiView):
    serializer_class = OrderAnalyticsSerializer
    permission_classes = [AbstractHasSpecificPermission(['analytics.view_orderanalytics'])]
    filterset_fields = ['date']
    ordering_fields = ['date', 'total_revenue', 'total_orders']
    ordering = ['-date']
    
    def get_queryset(self):
        return OrderAnalytics.objects.filter(is_deleted=False)
    
    @action(detail=False, methods=['get'])
    def order_trends(self, request):
        """Get order trends over time."""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        analytics = OrderAnalytics.objects.filter(
            date__gte=start_date, is_deleted=False
        ).order_by('date')
        
        serializer = OrderAnalyticsSerializer(analytics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def order_summary(self, request):
        """Get overall order summary."""
        total_orders = OrderAnalytics.objects.filter(is_deleted=False).aggregate(
            total=Sum('total_orders'),
            completed=Sum('completed_orders'),
            cancelled=Sum('cancelled_orders'),
            revenue=Sum('total_revenue')
        )
        
        return Response({
            'total_orders': total_orders['total'] or 0,
            'completed_orders': total_orders['completed'] or 0,
            'cancelled_orders': total_orders['cancelled'] or 0,
            'total_revenue': total_orders['revenue'] or 0
        })


class OrderAnalyticsCreateApiView(generics.CreateAPIView):
    serializer_class = OrderAnalyticsCreateSerializer
    permission_classes = [AbstractHasSpecificPermission(['analytics.add_orderanalytics'])]


class BusinessMetricsApiView(AbstractBaseListApiView):
    serializer_class = BusinessMetricsSerializer
    permission_classes = [AbstractHasSpecificPermission(['analytics.view_businessmetrics'])]
    filterset_fields = ['date']
    ordering_fields = ['date', 'gross_merchandise_volume', 'net_revenue']
    ordering = ['-date']
    
    def get_queryset(self):
        return BusinessMetrics.objects.filter(is_deleted=False)
    
    @action(detail=False, methods=['get'])
    def revenue_trends(self, request):
        """Get revenue trends over time."""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        metrics = BusinessMetrics.objects.filter(
            date__gte=start_date, is_deleted=False
        ).order_by('date')
        
        serializer = BusinessMetricsSerializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def revenue_summary(self, request):
        """Get overall revenue summary."""
        summary = BusinessMetrics.objects.filter(is_deleted=False).aggregate(
            gross_merchandise_volume=Sum('gross_merchandise_volume'),
            net_revenue=Sum('net_revenue'),
            profit_margin=Avg('profit_margin')
        )
        
        return Response({
            'gross_merchandise_volume': summary['gross_merchandise_volume'] or 0,
            'net_revenue': summary['net_revenue'] or 0,
            'average_profit_margin': round(summary['profit_margin'] or 0, 2)
        })


class BusinessMetricsCreateApiView(generics.CreateAPIView):
    serializer_class = BusinessMetricsCreateSerializer
    permission_classes = [AbstractHasSpecificPermission(['analytics.add_businessmetrics'])]


class PerformanceMetricsApiView(AbstractBaseListApiView):
    serializer_class = PerformanceMetricsSerializer
    permission_classes = [AbstractHasSpecificPermission(['analytics.view_performancemetrics'])]
    filterset_fields = ['date', 'time_period']
    ordering_fields = ['date', 'average_response_time', 'error_rate']
    ordering = ['-date']
    
    def get_queryset(self):
        return PerformanceMetrics.objects.filter(is_deleted=False)
    
    @action(detail=False, methods=['get'])
    def performance_summary(self, request):
        """Get overall performance summary."""
        summary = PerformanceMetrics.objects.filter(is_deleted=False).aggregate(
            avg_response_time=Avg('average_response_time'),
            total_errors=Sum('total_errors'),
            avg_error_rate=Avg('error_rate'),
            avg_cpu_usage=Avg('cpu_usage'),
            avg_memory_usage=Avg('memory_usage')
        )
        
        return Response({
            'average_response_time': round(summary['avg_response_time'] or 0, 2),
            'total_errors': summary['total_errors'] or 0,
            'average_error_rate': round(summary['avg_error_rate'] or 0, 2),
            'average_cpu_usage': round(summary['avg_cpu_usage'] or 0, 2),
            'average_memory_usage': round(summary['avg_memory_usage'] or 0, 2)
        })


class PerformanceMetricsCreateApiView(generics.CreateAPIView):
    serializer_class = PerformanceMetricsCreateSerializer
    permission_classes = [AbstractHasSpecificPermission(['analytics.add_performancemetrics'])]


class DashboardApiView(generics.GenericAPIView):
    permission_classes = [AbstractHasSpecificPermission(['analytics.view_servicecategoryanalytics'])]
    
    def get(self, request):
        """Get dashboard overview data."""
        # Get current month data
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Service category analytics
        category_analytics = ServiceCategoryAnalytics.objects.filter(
            date__gte=month_start, is_deleted=False
        ).aggregate(
            total_orders=Sum('order_count'),
            total_revenue=Sum('total_revenue'),
            avg_order_value=Avg('average_order_value')
        )
        
        # Order analytics
        order_analytics = OrderAnalytics.objects.filter(
            date__gte=month_start, is_deleted=False
        ).aggregate(
            total_orders=Sum('total_orders'),
            completed_orders=Sum('completed_orders'),
            total_revenue=Sum('total_revenue')
        )
        
        # Business metrics
        business_metrics = BusinessMetrics.objects.filter(
            date__gte=month_start, is_deleted=False
        ).aggregate(
            gross_merchandise_volume=Sum('gross_merchandise_volume'),
            net_revenue=Sum('net_revenue')
        )
        
        return Response({
            'current_month': {
                'category_analytics': {
                    'total_orders': category_analytics['total_orders'] or 0,
                    'total_revenue': category_analytics['total_revenue'] or 0,
                    'average_order_value': round(category_analytics['avg_order_value'] or 0, 2)
                },
                'order_analytics': {
                    'total_orders': order_analytics['total_orders'] or 0,
                    'completed_orders': order_analytics['completed_orders'] or 0,
                    'total_revenue': order_analytics['total_revenue'] or 0
                },
                'business_metrics': {
                    'gross_merchandise_volume': business_metrics['gross_merchandise_volume'] or 0,
                    'net_revenue': business_metrics['net_revenue'] or 0
                }
            }
        })
