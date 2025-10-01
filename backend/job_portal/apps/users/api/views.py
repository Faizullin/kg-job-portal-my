from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .permissions import HasMasterProfile, HasEmployerProfile
from .serializers import (
    EmployerProfileCreateUpdateSerializer,
    MasterProfileCreateUpdateSerializer, MasterSkillSerializer, PortfolioItemSerializer, SkillDetailSerializer,
    CertificateSerializer, ProfessionSerializer, PublicMasterProfileDetailSerializer, PublicMasterProfileSerializer,
)
from ..models import (
    Employer, Skill, Profession, Master,
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


class EmployerProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = EmployerProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create employer profile."""

        response = super().create(request, *args, **kwargs)
        assign_client_permissions(request.user)
        return response


class EmployerProfileRetrieveUpdateAPIView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = EmployerProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated, HasEmployerProfile]

    def get_object(self) -> Employer:
        return self.request.user.employer_profile


class MasterProfileCreateAPIView(
    generics.CreateAPIView
):
    serializer_class = MasterProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create service provider profile."""

        response = super().create(request, *args, **kwargs)
        assign_service_provider_permissions(request.user)
        return response


class MasterProfileRetrieveUpdateAPIView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = MasterProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated, HasMasterProfile]

    def get_object(self):
        return self.request.user.master_profile


class MasterSkillAPIViewSet(ModelViewSet):
    """Crud for service master skills."""

    serializer_class = MasterSkillSerializer
    permission_classes = [IsAuthenticated, HasMasterProfile]

    def get_queryset(self):
        provider_profile = self.request.user.master_profile
        return provider_profile.master_skills


class MasterPortfolioAPIViewSet(ModelViewSet):
    """Crud for service master portfolio items."""

    serializer_class = PortfolioItemSerializer
    permission_classes = [IsAuthenticated, HasMasterProfile]

    def get_queryset(self):
        provider_profile = self.request.user.master_profile
        return provider_profile.portfolio_items.select_related("skill_used")


class CertificateAPIViewSet(ModelViewSet):
    """Crud for certificates."""

    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated, HasMasterProfile]

    def get_queryset(self):
        provider_profile = self.request.user.master_profile
        return provider_profile.certificates.all()


class PublicSkillListAPIView(generics.ListAPIView):
    """List all available skills."""

    serializer_class = SkillDetailSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return Skill.objects.filter(is_active=True).select_related("category")


class PublicProfessionAPIViewSet(ReadOnlyModelViewSet):
    serializer_class = ProfessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "category": ["exact"],
        "is_active": ["exact"],
        "id": ["in"],
    }
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return Profession.objects.filter(is_active=True).select_related("category")


class PublicMasterProfileAPIViewSet(ReadOnlyModelViewSet):
    serializer_class = PublicMasterProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "id": ["in"],
    }

    def get_queryset(self):
        return Master.objects.select_related('user', 'profession').filter(user__is_active=True)

    @extend_schema(
        description="Master Profile Details",
        responses={200: PublicMasterProfileDetailSerializer(many=True)},
        operation_id="v1_users_masters_details"
    )
    @action(detail=True, methods=['get'])
    def details(self, request):
        obj = self.get_object()
        return Response(PublicMasterProfileDetailSerializer(instance=obj).data)


class MasterUpdateOnlineStatusAPIView(APIView):
    """Update online status for service provider."""

    permission_classes = [IsAuthenticated, HasMasterProfile]

    @extend_schema(
        description="Update online status",
        responses={
            200: OpenApiResponse(response={
                "message": "",
                "data": {

                }
            }),
        },
    )
    def post(self, request):
        """Update online status for service provider."""

        is_online = request.data.get('is_online', False)
        provider_profile: Master = request.user.master_profile
        provider_profile.is_online = is_online
        provider_profile.last_seen = timezone.now()
        provider_profile.save(update_fields=['is_online', 'last_seen'])
        provider_profile.save(update_fields=['is_online', 'last_seen'])
        return Response({
            'message': 'Online status updated successfully',
            'is_online': is_online,
            'last_seen': provider_profile.last_seen
        }, status=status.HTTP_200_OK)
