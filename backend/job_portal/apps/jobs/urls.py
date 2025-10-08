from django.urls import include, path
from rest_framework.routers import DefaultRouter

from job_portal.apps.reviews.api.views import ReviewListForJobAPIView
from .api.views import (
    AssignmentAttachmentAPIViewSet,
    JobAPIViewSet,
    JobApplicationAPIViewSet,
    JobAssignmentViewSet,
    JobAttachmentAPIViewSet,
)

router = DefaultRouter()
router.register(r"api/v1/jobs", JobAPIViewSet, basename="jobs")
router.register(
    r"api/v1/applications", JobApplicationAPIViewSet, basename="applications"
)
router.register(r"api/v1/assignments", JobAssignmentViewSet, basename="assignments")
router.register(
    "api/v1/jobs/(?P<job_id>[^/.]+)/attachments",
    JobAttachmentAPIViewSet,
    basename="job_attachments",
)
router.register(
    "api/v1/assignments/(?P<assignment_id>[^/.]+)/attachments",
    AssignmentAttachmentAPIViewSet,
    basename="assignment_attachments",
)

app_name = "jobs"

urlpatterns = [
    path("", include(router.urls)),
    path(
        "api/v1/jobs/<int:job_id>/reviews/",
        ReviewListForJobAPIView.as_view(),
        name="job-reviews-list",
    ),
]
