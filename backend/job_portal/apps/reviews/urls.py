from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.views import ReviewAPIViewSet

router = DefaultRouter()
router.register(r'api/v1/reviews', ReviewAPIViewSet, basename='reviews')

app_name = "reviews"

urlpatterns = [
    path("", include(router.urls)),
]
