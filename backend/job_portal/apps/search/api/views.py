from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from job_portal.apps.core.models import ServiceCategory
from job_portal.apps.jobs.models import Job, JobStatus
from job_portal.apps.users.api.permissions import HasEmployerProfile
from job_portal.apps.users.models import Master
from .serializers import (
    MasterSearchSerializer,
    JobSearchSerializer,
    MasterRecommendationSerializer,
    ServiceCategoryWithCountSerializer,
    HomePageDataSerializer
)


@extend_schema(
    responses={200: MasterSearchSerializer(many=True)},
    summary="Search for masters",
    description="Search masters by keywords, profession, location, and other criteria. "
                "Returns paginated list of master profiles with portfolio items and skills.",
)
class MasterSearchAPIView(generics.ListAPIView):
    """Search masters with optimized queryset and serializer."""

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
        """Get available masters with optimized queryset."""
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
                "portfolio_items",
                "master_skills",
                "master_skills__skill",
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


class HomeClientAPIView(APIView):
    """Recommendation system for clients"""

    permission_classes = [IsAuthenticated, HasEmployerProfile]

    @extend_schema(
        responses={200: HomePageDataSerializer},
        summary="Get home page data with master recommendations",
        description="Returns featured categories, recommended masters, and statistics for the home page. "
                    "Prioritizes top masters first, then fills with additional masters if needed.",
    )
    def get(self, request):
        """Get recommended masters based on employer preferences and location."""

        # Get featured service categories with master count annotation
        featured_categories = ServiceCategory.objects.filter(
            is_active=True,
            featured=True
        ).annotate(
            master_count=Count(
                'subcategories__providers_offering_service',
                distinct=True
            )
        ).order_by('sort_order', 'name')[:6]

        # Recommendation algorithm based on Master model fields
        # First, get top masters (preferred)
        top_masters = Master.objects.filter(
            user__is_active=True,
            is_available=True,
            is_top_master=True,
        ).select_related(
            'user',
            'profession',
            'statistics'
        ).prefetch_related(
            'services_offered',
            'services_offered__category'
        ).order_by(
            '-is_verified_provider',  # Prioritize verified providers
            '-statistics__average_rating',  # Order by rating
            '-statistics__total_reviews'  # Then by review count
        )

        # If we have less than 10 top masters, load additional masters
        top_masters_list = list(top_masters)
        if len(top_masters_list) < 10:
            # Get additional masters (not top masters) to fill up to 10
            additional_masters = Master.objects.filter(
                user__is_active=True,
                is_available=True,
                is_top_master=False,
            ).exclude(
                id__in=[master.id for master in top_masters_list]  # Exclude already loaded
            ).select_related(
                'user',
                'profession',
                'statistics'
            ).prefetch_related(
                'services_offered',
                'services_offered__category'
            ).order_by(
                '-is_verified_provider',  # Prioritize verified providers
                '-statistics__average_rating',  # Order by rating
                '-statistics__total_reviews'  # Then by review count
            )[:10 - len(top_masters_list)]

            # Combine top masters with additional masters
            recommended_masters = list(top_masters_list) + list(additional_masters)
        else:
            recommended_masters = top_masters_list[:10]

        # Get total counts
        total_masters_count = Master.objects.filter(
            user__is_active=True,
            is_available=True
        ).count()

        total_jobs_count = Job.objects.filter(
            status=JobStatus.PUBLISHED
        ).count()

        # Serialize data using nested serializers
        categories_data = ServiceCategoryWithCountSerializer(featured_categories, many=True).data
        masters_data = MasterRecommendationSerializer(recommended_masters, many=True).data

        # Prepare response data using HomePageDataSerializer
        response_data = {
            'featured_categories': categories_data,
            'recommended_masters': masters_data,
            'user_location': 'Алматы',  # Default location, can be made dynamic
            'total_masters_count': total_masters_count,
            'total_jobs_count': total_jobs_count,
        }

        serializer = HomePageDataSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
