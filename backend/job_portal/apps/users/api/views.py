from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.exceptions import StandardizedViewMixin
from utils.permissions import HasServiceProviderProfile

from ..models import (
    Certificate,
    ClientProfile,
    MasterSkill,
    PortfolioItem,
    Profession,
    ProviderStatistics,
    ServiceProviderProfile,
    ServiceProviderSkill,
)
from .serializers import (
    AdvancedUserProfileRetrieveUpdateSerializer,
    CertificateCreateUpdateSerializer,
    CertificateDetailSerializer,
    ClientProfileCreateUpdateSerializer,
    MasterSkillDetailSerializer,
    PortfolioItemCreateUpdateSerializer,
    PortfolioItemDetailSerializer,
    ProfessionSerializer,
    ProviderStatisticsSerializer,
    ServiceProviderProfileDetailSerializer,
    ServiceProviderProfileUpdateSerializer,
    ServiceProviderSkillCreateUpdateSerializer,
    ServiceProviderSkillDetailSerializer,
)


def assign_client_permissions(user):
    """Assign client-specific permissions to user."""
    client_group, _ = Group.objects.get_or_create(name="client")
    user.groups.add(client_group)
    permissions = Permission.objects.filter(
        codename__in=[
            "add_order",
            "view_order",
            "change_order",
            "view_bid",
            "add_payment",
            "view_payment",
        ]
    )
    for perm in permissions:
        user.user_permissions.add(perm)


def assign_service_provider_permissions(user):
    """Assign service provider-specific permissions to user."""
    provider_group, _ = Group.objects.get_or_create(name="service_provider")
    user.groups.add(provider_group)
    permissions = Permission.objects.filter(
        codename__in=["view_order", "add_bid", "view_bid", "change_bid", "view_payment"]
    )
    for perm in permissions:
        user.user_permissions.add(perm)


class AdvancedUserProfileRetrieveUpdateAPIView(
    StandardizedViewMixin, generics.RetrieveUpdateAPIView
):
    permission_classes = [IsAuthenticated]
    serializer_class = AdvancedUserProfileRetrieveUpdateSerializer

    def get_object(self):
        return self.request.user.job_portal_profile


class ClientProfileCreateAPIView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = ClientProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create client profile."""
        user_profile = request.user.job_portal_profile

        if ClientProfile.objects.filter(user_profile=user_profile).exists():
            raise ValidationError("Client profile already exists.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data.copy()
        preferred_services = validated_data.pop("preferred_services", None)
        client_profile = ClientProfile.objects.create(
            user_profile=user_profile, **validated_data
        )
        if preferred_services is not None:
            client_profile.preferred_services.set(preferred_services)

        assign_client_permissions(request.user)

        return Response(
            {"message": "Client profile created successfully."},
            status=status.HTTP_201_CREATED,
        )


class ClientProfileRetrieveUpdateAPIView(
    StandardizedViewMixin, generics.RetrieveUpdateAPIView
):
    serializer_class = ClientProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.job_portal_profile.client_profile


class ServiceProviderProfileCreateAPIView(
    StandardizedViewMixin, generics.CreateAPIView
):
    serializer_class = ServiceProviderProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create service provider profile."""
        user_profile = request.user.job_portal_profile

        if ServiceProviderProfile.objects.filter(user_profile=user_profile).exists():
            raise ValidationError("Service provider profile already exists.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data.copy()
        service_areas = validated_data.pop("service_areas", None)
        services_offered = validated_data.pop("services_offered", None)

        provider_profile = ServiceProviderProfile.objects.create(
            user_profile=user_profile, **validated_data
        )

        if service_areas is not None:
            provider_profile.service_areas.set(service_areas)
        if services_offered is not None:
            provider_profile.services_offered.set(services_offered)

        assign_service_provider_permissions(request.user)

        return Response(
            {"message": "Service provider profile created successfully."},
            status=status.HTTP_201_CREATED,
        )


class ServiceProviderProfileRetrieveUpdateAPIView(
    StandardizedViewMixin, generics.RetrieveUpdateAPIView
):
    serializer_class = ServiceProviderProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.job_portal_profile.service_provider_profile


class ServiceProviderRetrieveAPIView(StandardizedViewMixin, generics.RetrieveAPIView):
    """Retrieve service provider details for public viewing."""
    serializer_class = ServiceProviderProfileDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ServiceProviderProfile.objects.filter(
            is_available=True
        ).select_related(
            "user_profile__user",
            "profession"
        ).prefetch_related(
            "provider_skills__skill",
            "portfolio_items",
            "certificates",
            "statistics"
        )


class ServiceProviderSkillAPIView(StandardizedViewMixin, generics.ListCreateAPIView):
    """List and create service provider skills."""
    serializer_class = ServiceProviderSkillDetailSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]

    def get_queryset(self):
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        return ServiceProviderSkill.objects.filter(
            service_provider=provider_profile
        ).select_related("skill")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ServiceProviderSkillCreateUpdateSerializer
        return ServiceProviderSkillDetailSerializer

    def perform_create(self, serializer):
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        serializer.save(service_provider=provider_profile)


class MasterSkillListAPIView(StandardizedViewMixin, generics.ListAPIView):
    """List all available master skills."""
    serializer_class = MasterSkillDetailSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return MasterSkill.objects.filter(is_active=True).select_related("category")


class PortfolioItemListCreateAPIView(
    StandardizedViewMixin, generics.ListCreateAPIView
):
    """List and create portfolio items."""
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]

    def get_queryset(self):
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        return PortfolioItem.objects.filter(
            service_provider=provider_profile
        ).select_related("skill_used")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PortfolioItemCreateUpdateSerializer
        return PortfolioItemDetailSerializer

    def perform_create(self, serializer):
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        serializer.save(service_provider=provider_profile)


class PortfolioItemRetrieveUpdateDestroyAPIView(
    StandardizedViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    """Retrieve, update, and delete portfolio items."""
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]

    def get_queryset(self):
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        return PortfolioItem.objects.filter(
            service_provider=provider_profile
        ).select_related("skill_used")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PortfolioItemDetailSerializer
        return PortfolioItemCreateUpdateSerializer


class CertificateListCreateAPIView(StandardizedViewMixin, generics.ListCreateAPIView):
    """List and create certificates."""
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]

    def get_queryset(self):
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        return Certificate.objects.filter(service_provider=provider_profile)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CertificateCreateUpdateSerializer
        return CertificateDetailSerializer

    def perform_create(self, serializer):
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        serializer.save(service_provider=provider_profile)


class CertificateRetrieveUpdateDestroyAPIView(
    StandardizedViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    """Retrieve, update, and delete certificates."""
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]

    def get_queryset(self):
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        return Certificate.objects.filter(service_provider=provider_profile)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CertificateDetailSerializer
        return CertificateCreateUpdateSerializer


class ProfessionListAPIView(StandardizedViewMixin, generics.ListAPIView):
    """List all available professions."""
    serializer_class = ProfessionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return Profession.objects.filter(is_active=True).select_related("category")


class ProviderStatisticsRetrieveAPIView(
    StandardizedViewMixin, generics.RetrieveAPIView
):
    """Retrieve provider statistics."""
    serializer_class = ProviderStatisticsSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]

    def get_object(self):
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        statistics, created = ProviderStatistics.objects.get_or_create(
            provider=provider_profile
        )
        return statistics


class UpdateOnlineStatusAPIView(StandardizedViewMixin, APIView):
    """Update user's online status."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Update online status for service provider."""
        is_online = request.data.get('is_online', False)
        
        try:
            provider_profile = request.user.job_portal_profile.service_provider_profile
            provider_profile.is_online = is_online
            provider_profile.last_seen = timezone.now()
            provider_profile.save(update_fields=['is_online', 'last_seen'])
            
            return Response({
                'message': 'Online status updated successfully',
                'is_online': is_online,
                'last_seen': provider_profile.last_seen
            }, status=status.HTTP_200_OK)
            
        except AttributeError:
            return Response({
                'error': 'Service provider profile not found'
            }, status=status.HTTP_404_NOT_FOUND)


class GetUserRatingAPIView(StandardizedViewMixin, APIView):
    """Get user rating (for clients)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Get user rating."""
        try:
            from job_portal.apps.orders.models import OrderAssignment
            
            # Get user's client profile
            user_profile = request.user.job_portal_profile
            client_profile = user_profile.client_profile
            
            # Calculate average rating from completed orders
            assignments = OrderAssignment.objects.filter(
                order__client=client_profile,
                client_rating__isnull=False
            )
            
            if assignments.exists():
                avg_rating = assignments.aggregate(
                    avg_rating=models.Avg('client_rating')
                )['avg_rating']
                total_reviews = assignments.count()
            else:
                avg_rating = 0.0
                total_reviews = 0
            
            return Response({
                'user_id': request.user.id,
                'username': request.user.username,
                'average_rating': round(float(avg_rating), 1),
                'total_reviews': total_reviews
            }, status=status.HTTP_200_OK)
            
        except AttributeError:
            return Response({
                'error': 'Client profile not found'
            }, status=status.HTTP_404_NOT_FOUND)