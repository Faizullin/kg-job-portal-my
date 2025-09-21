from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.permissions import IsAuthenticated
from utils.permissions import HasSpecificPermission
from utils.pagination import CustomPagination
from ..models import UserActivity, OrderAnalytics, ServiceCategoryAnalytics, PerformanceMetrics, BusinessMetrics
from .serializers import (
    UserActivitySerializer, OrderAnalyticsSerializer, ServiceCategoryAnalyticsSerializer,
    PerformanceMetricsSerializer, BusinessMetricsSerializer, UserActivityCreateSerializer,
    ServiceCategoryAnalyticsCreateSerializer, OrderAnalyticsCreateSerializer,DashboardResponseSerializer
)


class UserActivityApiView(generics.ListAPIView):
    serializer_class = UserActivitySerializer
    permission_classes = [HasSpecificPermission(['analytics.add_useractivity'])]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activity_type', 'user', 'ip_address']
    search_fields = ['description', 'user__username']
    ordering_fields = ['created_at', 'activity_type']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Manager automatically filters out deleted objects
        return UserActivity.objects.all().select_related('user')
    
    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """Get recent user activities (last 24 hours)."""
        yesterday = timezone.now() - timedelta(days=1)
        
        # Manager automatically filters out deleted objects
        activities = UserActivity.objects.filter(
            created_at__gte=yesterday
        ).select_related('user')[:100]
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_summary(self, request):
        """Get activity summary for a specific user."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)
        
        # Manager automatically filters out deleted objects
        activities = UserActivity.objects.filter(
            user_id=user_id
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
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class ServiceCategoryAnalyticsApiView(generics.ListAPIView):
    serializer_class = ServiceCategoryAnalyticsSerializer
    permission_classes = [HasSpecificPermission(['analytics.add_servicecategoryanalytics'])]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category', 'date']
    ordering_fields = ['date', 'total_revenue', 'order_count']
    ordering = ['-date']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Manager automatically filters out deleted objects
        return ServiceCategoryAnalytics.objects.all().select_related('category')
    
    @action(detail=False, methods=['get'])
    def top_performing_categories(self, request):
        """Get top performing service categories by revenue."""
        # Manager automatically filters out deleted objects
        categories = ServiceCategoryAnalytics.objects.all().select_related('category').order_by('-total_revenue')[:10]
        
        serializer = ServiceCategoryAnalyticsSerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def category_comparison(self, request):
        """Compare service categories performance."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({'error': 'start_date and end_date are required'}, status=400)
        
        # Manager automatically filters out deleted objects
        metrics = ServiceCategoryAnalytics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).select_related('category')
        
        serializer = ServiceCategoryAnalyticsSerializer(metrics, many=True)
        return Response(serializer.data)


class ServiceCategoryAnalyticsCreateApiView(generics.CreateAPIView):
    serializer_class = ServiceCategoryAnalyticsCreateSerializer
    permission_classes = [HasSpecificPermission(['analytics.add_servicecategoryanalytics'])]


class OrderAnalyticsApiView(generics.ListAPIView):
    serializer_class = OrderAnalyticsSerializer
    permission_classes = [HasSpecificPermission(['analytics.add_orderanalytics'])]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['date']
    ordering_fields = ['date', 'total_revenue', 'total_orders']
    ordering = ['-date']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return OrderAnalytics.objects.all()
    
    @action(detail=False, methods=['get'])
    def order_trends(self, request):
        """Get order trends over time."""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        analytics = OrderAnalytics.objects.filter(
            date__gte=start_date,
        ).order_by('date')
        
        serializer = OrderAnalyticsSerializer(analytics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def order_summary(self, request):
        """Get overall order summary."""
        total_orders = OrderAnalytics.objects.aggregate(
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
    permission_classes = [HasSpecificPermission(['analytics.add_orderanalytics'])]


class BusinessMetricsApiView(generics.ListAPIView):
    serializer_class = BusinessMetricsSerializer
    permission_classes = [HasSpecificPermission(['analytics.add_businessmetrics'])]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['date']
    ordering_fields = ['date', 'gross_merchandise_volume', 'net_revenue']
    ordering = ['-date']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return BusinessMetrics.objects.all()
    
    @action(detail=False, methods=['get'])
    def revenue_trends(self, request):
        """Get revenue trends over time."""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        metrics = BusinessMetrics.objects.filter(
            date__gte=start_date,
        ).order_by('date')
        
        serializer = BusinessMetricsSerializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def revenue_summary(self, request):
        """Get overall revenue summary."""
        summary = BusinessMetrics.objects.aggregate(
            gross_merchandise_volume=Sum('gross_merchandise_volume'),
            net_revenue=Sum('net_revenue'),
            profit_margin=Avg('profit_margin')
        )
        
        return Response({
            'gross_merchandise_volume': summary['gross_merchandise_volume'] or 0,
            'net_revenue': summary['net_revenue'] or 0,
            'average_profit_margin': round(summary['profit_margin'] or 0, 2)
        })

class PerformanceMetricsApiView(generics.ListAPIView):
    serializer_class = PerformanceMetricsSerializer
    permission_classes = [HasSpecificPermission(['analytics.add_performancemetrics'])]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['date', 'time_period']
    ordering_fields = ['date', 'average_response_time', 'error_rate']
    ordering = ['-date']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return PerformanceMetrics.objects.all()
    
    @action(detail=False, methods=['get'])
    def performance_summary(self, request):
        """Get overall performance summary."""
        summary = PerformanceMetrics.objects.aggregate(
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


class DashboardApiView(generics.GenericAPIView):
    serializer_class = DashboardResponseSerializer
    permission_classes = [HasSpecificPermission(['analytics.add_servicecategoryanalytics'])]
    
    def get(self, request):
        """Get dashboard overview data."""
        # Get current month data
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Service category analytics
        category_analytics = ServiceCategoryAnalytics.objects.filter(
            date__gte=month_start,
        ).aggregate(
            total_orders=Sum('order_count'),
            total_revenue=Sum('total_revenue'),
            avg_order_value=Avg('average_order_value')
        )
        
        # Order analytics
        order_analytics = OrderAnalytics.objects.filter(
            date__gte=month_start,
        ).aggregate(
            total_orders=Sum('total_orders'),
            completed_orders=Sum('completed_orders'),
            total_revenue=Sum('total_revenue')
        )
        
        # Business metrics
        business_metrics = BusinessMetrics.objects.filter(
            date__gte=month_start,
        ).aggregate(
            gross_merchandise_volume=Sum('gross_merchandise_volume'),
            net_revenue=Sum('net_revenue')
        )
        
        response_data = {
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
        }
        
        serializer = self.get_serializer(response_data)
        return Response(serializer.data)
