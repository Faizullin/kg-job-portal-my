from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.views import (
    EmployerProfileRetrieveUpdateAPIView,
    MasterSkillAPIViewSet,
    MasterProfileCreateAPIView, EmployerProfileCreateAPIView,
    MasterProfileRetrieveUpdateAPIView, MasterPortfolioAPIViewSet, PublicSkillListAPIView,
    PublicMasterProfileAPIViewSet, CertificateAPIViewSet, MasterUpdateOnlineStatusAPIView,
    PublicProfessionAPIViewSet,
)

router = DefaultRouter()
router.register(r'api/v1/users/my/skills', MasterSkillAPIViewSet, basename='my-skills')
router.register(r'api/v1/users/my/portfolio', MasterPortfolioAPIViewSet, basename='my-portfolio')
router.register(r'api/v1/users/my/certificates', CertificateAPIViewSet, basename='my-certificates')
router.register(r"api/v1/users/professions", PublicProfessionAPIViewSet, basename='public-professions')
router.register(r"api/v1/users/masters", PublicMasterProfileAPIViewSet, basename='public-masters')

app_name = "users"

urlpatterns = [
    path(
        "api/v1/users/my/employer/create/",
        EmployerProfileCreateAPIView.as_view(),
        name="my-employer-create",
    ),
    path(
        "api/v1/users/my/master/create",
        MasterProfileCreateAPIView.as_view(),
        name="my-master-create",
    ),
    path(
        "api/v1/users/my/employer/",
        EmployerProfileRetrieveUpdateAPIView.as_view(),
        name="my-employer-retrieve-update",
    ),
    path(
        "api/v1/users/my/master/",
        MasterProfileRetrieveUpdateAPIView.as_view(),
        name="my-master-retrieve-update",
    ),
    path(
        "api/v1/users/my/status",
        MasterUpdateOnlineStatusAPIView.as_view(),
        name="my-master-update-online-status",
    ),
    path("", include(router.urls)),

    # Reference Data (Public)
    path(
        "api/v1/users/skills/", PublicSkillListAPIView.as_view(), name="public-skill-list"
    ),
]
