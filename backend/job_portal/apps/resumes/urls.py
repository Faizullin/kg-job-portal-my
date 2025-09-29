from django.urls import path, include
from rest_framework.routers import DefaultRouter

from job_portal.apps.resumes.api.views import MasterResumeAPIViewSet

router = DefaultRouter()
router.register(r"api/v1/resumes", MasterResumeAPIViewSet, basename="master-resume")

app_name = "resumes"

urlpatterns = [
    path("", include(router.urls)),
]
