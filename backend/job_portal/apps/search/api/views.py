from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from job_portal.apps.core.models import ServiceCategory
from job_portal.apps.users.models import Employer, Master
from .serializers import (
    ClientDashboardResponseSerializer,
    OrderSerializer,
    ServiceProviderSearchListSerializer,
)
from ...jobs.models import Job


class ClientDashboardApiView(APIView):
    """Client dashboard API - provides data specific to clients."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get client dashboard data",
        description="Retrieve dashboard data specific to clients including top providers, service categories, and recent orders.",
        responses={
            200: ClientDashboardResponseSerializer,
            401: OpenApiResponse(description="Authentication required"),
            500: OpenApiResponse(description="Internal server error"),
        },
    )
    def get(self, request):
        """Get client dashboard data."""
        try:
            user = request.user
            client_profile: Employer = user.job_portal_profile.client_profile

            # Get featured categories - prioritize client's preferred service categories
            preferred_category_ids = set(
                client_profile.preferred_services.values_list("category_id", flat=True)
            )

            # First, get preferred categories that are featured
            preferred_featured = ServiceCategory.objects.filter(
                is_active=True, featured=True, id__in=preferred_category_ids
            ).order_by("sort_order", "name")

            # Then, get other featured categories to fill up to 7 items
            remaining_count = 7 - preferred_featured.count()
            other_featured = (
                ServiceCategory.objects.filter(is_active=True, featured=True)
                .exclude(id__in=preferred_category_ids)
                .order_by("sort_order", "name")[:remaining_count]
            )

            # Combine both querysets
            featured_categories = list(preferred_featured) + list(other_featured)

            # Get top providers (top masters) - prioritize those offering client's preferred services
            preferred_service_ids = list(
                client_profile.preferred_services.values_list("id", flat=True)
            )

            preferred_provider_profiles = (
                Master.objects.filter(
                    is_available=True,
                    is_top_master=True,
                    services_offered__id__in=preferred_service_ids,
                )
                .select_related(
                    "profession",
                    "statistics",
                    "user_profile__user",
                )
                .order_by(
                    "-statistics__average_rating",
                    "-statistics__total_reviews",
                )
                .distinct()
            )

            # Then, get other users with top providers to fill up to 5 items
            remaining_count = 5 - preferred_provider_profiles.count()
            other_provider_profiles = (
                Master.objects.filter(
                    is_available=True,
                    is_top_master=True,
                )
                .exclude(services_offered__id__in=preferred_service_ids)
                .select_related(
                    "profession",
                    "statistics",
                    "user_profile__user",
                )
                .order_by(
                    "-statistics__average_rating",
                    "-statistics__total_reviews",
                )
                .distinct()[:remaining_count]
            )

            # Combine both querysets
            top_providers = list(preferred_provider_profiles) + list(
                other_provider_profiles
            )
            print("top_providers", top_providers, "preferred_service_ids", preferred_service_ids)

            # Get recent orders for this client
            recent_orders = (
                Job.objects.filter(client=client_profile)
                .select_related(
                    "service_subcategory__category", "client__user_profile__user"
                )
                .order_by("-created_at")[:5]
            )

            # Get platform statistics
            stats = self.get_client_stats()
            serializer = ClientDashboardResponseSerializer(
                {
                    "featured_categories": list(featured_categories),
                    "top_providers": list(top_providers),
                    "recent_orders": list(recent_orders),
                    "platform_stats": stats,
                }
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to load client dashboard data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_client_stats(self):
        """Get client-specific platform statistics."""
        try:
            # Get real statistics from database - focus on top masters
            total_providers = Master.objects.filter(
                is_available=True, is_top_master=True
            ).count()

            total_categories = ServiceCategory.objects.filter(
                is_active=True, featured=True
            ).count()

            # Calculate average rating from top masters only
            avg_rating_result = Master.objects.filter(
                is_available=True, is_top_master=True, statistics__isnull=False
            ).aggregate(avg_rating=Avg("statistics__average_rating"))

            avg_rating = avg_rating_result["avg_rating"] or 0

            # Get average response time from top masters
            avg_response_time = Master.objects.filter(
                is_available=True, is_top_master=True
            ).aggregate(avg_response=Avg("response_time_hours"))

            response_time_hours = avg_response_time["avg_response"] or 24

            return {
                "total_providers": total_providers,
                "total_categories": total_categories,
                "average_rating": round(float(avg_rating), 1),
                "response_time_hours": int(response_time_hours),
            }
        except Exception:
            return {
                "total_providers": 0,
                "total_categories": 0,
                "average_rating": 0.0,
                "response_time_hours": 24,
            }


# class ProviderDashboardApiView(APIView):
#     """Provider dashboard API - provides data specific to service providers."""

#     permission_classes = [IsAuthenticated, HasServiceProviderProfile]

#     @extend_schema(
#         summary="Get provider dashboard data",
#         description="Retrieve dashboard data specific to service providers including statistics, portfolio, reviews, and professional information.",
#         responses={
#             200: ProviderDashboardResponseSerializer,
#             401: OpenApiResponse(description="Authentication required"),
#             403: OpenApiResponse(description="Service provider profile required"),
#             500: OpenApiResponse(description="Internal server error"),
#         },
#     )
#     def get(self, request):
#         """Get provider dashboard data."""
#         try:
#             user = request.user
#             provider_profile: ServiceProviderProfile = user.job_portal_profile.service_provider_profile

#             # Get provider statistics
#             stats = self.get_provider_stats(provider_profile)

#             # Get recent reviews
#             recent_reviews = (
#                 Review.objects.filter(provider=provider_profile)
#                 .select_related("reviewer")
#                 .order_by("-created_at")[:5]
#             )
#             skills = provider_profile.provider_skills.select_related("skill").order_by(
#                 "-is_primary_skill", "skill__name"
#             )
#             certificates = provider_profile.certificates.order_by("-issue_date")[:10]

#             # Prepare data for serialization
#             provider_info_data = {
#                 "name": f"{user.first_name} {user.last_name}".strip() or user.username,
#                 "profession": provider_profile.profession.name
#                 if provider_profile.profession
#                 else "Специалист",
#                 "is_top_master": provider_profile.is_top_master,
#                 "is_verified": provider_profile.is_verified_provider,
#                 "avatar": user.photo_url,
#                 "location": provider_profile.current_location or "Бишкек",
#                 "is_online": provider_profile.is_online,
#             }

#             professional_info_data = {
#                 "work_experience_start_year": provider_profile.work_experience_start_year,
#                 "education_institution": provider_profile.education_institution or "",
#                 "education_years": provider_profile.education_years or "",
#                 "languages": provider_profile.languages
#                 if provider_profile.languages
#                 else [],
#                 "about_description": provider_profile.about_description or "",
#             }

#             # Serialize data
#             serializer = ProviderDashboardResponseSerializer(
#                 data={
#                     "provider_info": provider_info_data,
#                     "statistics": stats,
#                     "recent_reviews": recent_reviews,
#                     "skills": skills,
#                     "certificates": certificates,
#                     "professional_info": professional_info_data,
#                 }
#             )

#             if serializer.is_valid():
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 return Response(
#                     {"error": "Serialization failed", "details": serializer.errors},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#         except Exception as e:
#             return Response(
#                 {"error": f"Failed to load provider dashboard data: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#     def get_provider_stats(self, provider_profile):
#         """Get provider-specific statistics."""
#         try:
#             # Get statistics from the ProviderStatistics model
#             stats = provider_profile.statistics

#             return {
#                 "total_orders": stats.total_jobs_completed,
#                 "total_reviews": stats.total_reviews,
#                 "on_time_percentage": float(stats.on_time_percentage),
#                 "repeat_customer_percentage": float(stats.repeat_customer_percentage),
#                 "completed_jobs": stats.total_jobs_completed,
#                 "hourly_rate": f"{provider_profile.hourly_rate}₸/час"
#                 if provider_profile.hourly_rate
#                 else "Цена договорная",
#                 "response_time": f"{provider_profile.response_time_hours} часа"
#                 if provider_profile.response_time_hours
#                 else "24 часа",
#             }
#         except Exception:
#             return {
#                 "total_orders": 0,
#                 "total_reviews": 0,
#                 "on_time_percentage": 0.0,
#                 "repeat_customer_percentage": 0.0,
#                 "completed_jobs": 0,
#                 "hourly_rate": "Цена договорная",
#                 "response_time": "24 часа",
#             }


class ServiceProviderSearchAPIView(generics.ListAPIView):
    """Search service providers."""

    serializer_class = ServiceProviderSearchListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        "first_name",
        "last_name",
        "username",
        "profession__name",
        "services_offered__name",
        "services_offered__category__name",
    ]
    filterset_fields = {
        "profession": ["exact"],
        "services_offered__category": ["exact"],
        "is_top_master": ["exact"],
        "is_verified_provider": ["exact"],
    }
    ordering_fields = ["created_at"]
    ordering = ["-statistics__average_rating"]

    def get_queryset(self):
        """Get available service providers."""
        return (
            Master.objects.filter(is_available=True)
            .select_related(
                "user_profile__user",
                "profession",
                "statistics",
            )
            .prefetch_related(
                "services_offered",
                "services_offered__category",
                "provider_skills",
                "provider_skills__skill",
                "portfolio_items",
            )
            .distinct()
        )


class OrderSearchAPIView(generics.ListAPIView):
    """Search orders."""

    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        "title",
        "description",
        "city",
        "service_subcategory__name",
        "service_subcategory__category__name",
    ]
    filterset_fields = {
        "status": ["exact"],
        "city": ["icontains"],
        "service_subcategory__category": ["exact"],
        "budget_min": ["gte"],
        "budget_max": ["lte"],
        "urgency": ["exact"],
    }
    ordering_fields = ["created_at", "budget_min", "budget_max"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Get published orders."""
        return (
            Job.objects.filter(status__in=["published", "bidding"], is_deleted=False)
            .select_related(
                "service_subcategory",
                "service_subcategory__category",
                "client__user_profile__user",
            )
            .prefetch_related("photos", "bids__provider__user_profile__user")
        )
