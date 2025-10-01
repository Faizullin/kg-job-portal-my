from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from .serializers import MasterSearchSerializer, JobSearchSerializer
from job_portal.apps.jobs.models import Job, JobStatus
from job_portal.apps.users.models import Master


class MasterSearchAPIView(generics.ListAPIView):
    """Search masters with optimized search serializer."""

    serializer_class = MasterSearchSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "profession": ["exact"],
        "services_offered__category": ["exact"],
        "is_top_master": ["exact"],
        "is_verified_provider": ["exact"],
        "is_available": ["exact"],
    }
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__username",
        "profession__name",
        "services_offered__name",
        "services_offered__category__name",
        "current_location",
    ]
    ordering_fields = ["created_at", "statistics__average_rating"]
    ordering = ["-statistics__average_rating"]

    def get_queryset(self):
        """Get available masters."""
        return (
            Master.objects.filter(
                user__is_active=True,
                is_available=True,
            )
            .select_related(
                "user",
                "profession",
                "statistics",
            )
            .prefetch_related(
                "services_offered",
                "services_offered__category",
                "master_skills",
                "master_skills__skill",
                "portfolio_items",
            )
            .distinct()
        )


class JobSearchAPIView(generics.ListAPIView):
    """Search jobs with optimized search serializer."""

    serializer_class = JobSearchSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "status": ["exact"],
        "city": ["exact"],
        "service_subcategory__category": ["exact"],
        "budget_min": ["gte"],
        "budget_max": ["lte"],
        "urgency": ["exact"],
    }
    search_fields = [
        "title",
        "description",
        "city",
        "service_subcategory__name",
        "service_subcategory__category__name",
    ]
    ordering_fields = ["created_at", "budget_min", "budget_max"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Get published jobs."""
        return (
            Job.objects.filter(status=JobStatus.PUBLISHED)
            .select_related(
                "employer__user",
                "service_subcategory",
                "service_subcategory__category",
            )
            .prefetch_related("photos", "bids__provider__user")
        )
