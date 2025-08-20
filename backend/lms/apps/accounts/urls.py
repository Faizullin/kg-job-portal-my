from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import views as api_views

router = DefaultRouter()
router.register(r"api/v1/lms/accounts/users", api_views.UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
