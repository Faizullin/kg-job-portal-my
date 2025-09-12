from django.urls import path
from .api.views import (
    NotificationApiView, NotificationDetailApiView, NotificationCreateApiView,
    NotificationSettingApiView,
    NotificationTemplateApiView, NotificationTemplateDetailApiView, NotificationTemplateCreateApiView,
)

app_name = 'notifications'

urlpatterns = [
    # Notifications
    path('api/v1/notifications/', NotificationApiView.as_view(), name='notifications'),
    path('api/v1/notifications/create/', NotificationCreateApiView.as_view(), name='notification-create'),
    path('api/v1/notifications/<int:pk>/', NotificationDetailApiView.as_view(), name='notification-detail'),
    
    # Notification Settings (single user preference)
    path('api/v1/notifications/settings/', NotificationSettingApiView.as_view(), name='notification-settings'),
    
    # Notification Templates
    path('api/v1/notifications/templates/', NotificationTemplateApiView.as_view(), name='notification-templates'),
    path('api/v1/notifications/templates/create/', NotificationTemplateCreateApiView.as_view(), name='notification-template-create'),
    path('api/v1/notifications/templates/<int:pk>/', NotificationTemplateDetailApiView.as_view(), name='notification-template-detail'),
]
