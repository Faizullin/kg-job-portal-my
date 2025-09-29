from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.views import NotificationAPIViewSet

app_name = 'notifications'

router = DefaultRouter()
router.register(r'api/v1/notifications', NotificationAPIViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
]
