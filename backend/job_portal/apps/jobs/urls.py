from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.views import (
    JobAPIViewSet, JobApplicationAPIViewSet, JobAssignmentViewSet,
)

router = DefaultRouter()
router.register(r'api/v1/jobs', JobAPIViewSet, basename='jobs')
router.register(r'api/v1/applications', JobApplicationAPIViewSet, basename='applications')
router.register(r'api/v1/assignments', JobAssignmentViewSet, basename='assignments')

app_name = 'jobs'

urlpatterns = [
    path('', include(router.urls)),
]
