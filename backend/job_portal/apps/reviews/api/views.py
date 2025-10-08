from job_portal.apps.jobs.models import Job, JobAssignment
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError
from utils.pagination import CustomPagination

from ..models import Review
from .serializers import (
    ReviewCreateSerializer,
    ReviewSerializer,
    ReviewUpdateSerializer,
)


class ReviewListForJobAPIView(generics.ListAPIView):
    """List all reviews for a job."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        job = get_object_or_404(Job, id=self.kwargs.get("job_id"))
        return Review.objects.filter(job=job).select_related(
            "reviewer", "master__user", "job"
        )


class MyReviewsListAPIView(generics.ListAPIView):
    """List all reviews created by the authenticated user."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user).select_related(
            "reviewer", "master__user", "job"
        )


class AddReviewForJobDoneAPIView(generics.CreateAPIView):
    """Add a review for a job if it doesn't exist."""

    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.select_related("reviewer", "master__user", "job")

    def perform_create(self, serializer):
        assignment: JobAssignment = get_object_or_404(
            JobAssignment, id=serializer.validated_data.pop("assignment")
        )
        job = assignment.job
        master = assignment.master
        if Review.objects.filter(job=job, reviewer=self.request.user).exists():
            raise ValidationError("You have already reviewed this job.")
        serializer.save(reviewer=self.request.user, job=job, master=master)


class EditReviewForJobDoneAPIView(generics.UpdateAPIView):
    """Edit a review for a job."""

    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.select_related("reviewer", "master__user", "job")

    def perform_update(self, serializer):
        get_object_or_404(JobAssignment, id=serializer.validated_data.get("assignment"))
        if serializer.instance.reviewer != self.request.user:
            raise PermissionDenied
        serializer.save(reviewer=self.request.user)


class DeleteReviewForJobDoneAPIView(generics.DestroyAPIView):
    """Delete a review for a job."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.select_related("reviewer", "master__user", "job")

    def perform_destroy(self, instance):
        if instance.reviewer != self.request.user:
            raise PermissionDenied
        instance.delete()
