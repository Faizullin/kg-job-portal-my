from django.urls import path
from .api.views import (
    UserActivityApiView, UserActivityCreateApiView, ServiceCategoryAnalyticsApiView,
    ServiceCategoryAnalyticsCreateApiView, OrderAnalyticsApiView, OrderAnalyticsCreateApiView,
    BusinessMetricsApiView, BusinessMetricsCreateApiView, PerformanceMetricsApiView,
    DashboardApiView
)

app_name = 'analytics'

urlpatterns = [
    # Dashboard
    path('api/v1/analytics/dashboard/', DashboardApiView.as_view(), name='dashboard'),
    
    # User Activities
    path('api/v1/analytics/activities/', UserActivityApiView.as_view(), name='user-activities'),
    path('api/v1/analytics/activities/create/', UserActivityCreateApiView.as_view(), name='user-activity-create'),
    
    # Service Category Analytics
    path('api/v1/analytics/categories/', ServiceCategoryAnalyticsApiView.as_view(), name='service-category-analytics'),
    path('api/v1/analytics/categories/create/', ServiceCategoryAnalyticsCreateApiView.as_view(), name='service-category-analytics-create'),
    
    # Order Analytics
    path('api/v1/analytics/orders/', OrderAnalyticsApiView.as_view(), name='order-analytics'),
    path('api/v1/analytics/orders/create/', OrderAnalyticsCreateApiView.as_view(), name='order-analytics-create'),
    
    # Business Metrics
    path('api/v1/analytics/business/', BusinessMetricsApiView.as_view(), name='business-metrics'),
    path('api/v1/analytics/business/create/', BusinessMetricsCreateApiView.as_view(), name='business-metrics-create'),
    
    # Performance Metrics
    path('api/v1/analytics/performance/', PerformanceMetricsApiView.as_view(), name='performance-metrics'),
]
