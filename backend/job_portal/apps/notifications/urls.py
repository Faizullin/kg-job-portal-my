from django.urls import path
from .api.views import (
    NotificationApiView, NotificationDetailApiView, NotificationCreateApiView,
    NotificationUnreadView, NotificationRecentView, NotificationMarkAllReadView, NotificationCountView
)

app_name = 'notifications'

urlpatterns = [
    # Notifications
    path('api/v1/notifications/', NotificationApiView.as_view(), name='notifications'),
    path('api/v1/notifications/create/', NotificationCreateApiView.as_view(), name='notification-create'),
    path('api/v1/notifications/<int:pk>/', NotificationDetailApiView.as_view(), name='notification-detail'),
    
    # Additional notification endpoints
    path('api/v1/notifications/unread/', NotificationUnreadView.as_view(), name='notification-unread'),
    path('api/v1/notifications/recent/', NotificationRecentView.as_view(), name='notification-recent'),
    path('api/v1/notifications/mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('api/v1/notifications/count/', NotificationCountView.as_view(), name='notification-count'),
]
