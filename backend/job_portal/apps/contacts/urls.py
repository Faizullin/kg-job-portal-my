from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.views import SimpleContactAPIViewSet

app_name = "contacts"

router = DefaultRouter()
router.register(r'api/v1/contacts', SimpleContactAPIViewSet, basename='contacts')

urlpatterns = [
    path("", include(router.urls)),
]
