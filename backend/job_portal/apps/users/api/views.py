from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, mixins, viewsets, parsers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .permissions import HasMasterProfile, HasEmployerProfile
from .serializers import (
    EmployerProfileCreateUpdateSerializer,
    MasterProfileCreateUpdateSerializer, MasterSkillSerializer, PortfolioItemSerializer, SkillDetailSerializer,
    CertificateSerializer, ProfessionSerializer, PublicMasterProfileDetailSerializer, PublicMasterProfileSerializer,
    MasterOnlineStatusRequestSerializer, MasterOnlineStatusResponseSerializer, PortfolioItemAttachmentUploadSerializer,
)
from ..models import (
    Employer, MasterStatistics, Skill, Profession, Master, PortfolioItem,
)
from ...attachments.api.permissions import IsAttachmentOwner
from ...attachments.models import create_attachments
from ...attachments.serializers import AttachmentSerializer


def assign_client_permissions(user):
    """Assign client-specific permissions to user."""
    client_group, _ = Group.objects.get_or_create(name="client")
    user.groups.add(client_group)
    permissions = Permission.objects.filter(
        codename__in=[
            "add_job",
            "view_job",
            "change_job",
            "view_bid",
            "add_payment",
            "view_payment",
        ]
    )
    for perm in permissions:
        user.user_permissions.add(perm)


def assign_master_permissions(user):
    """Assign master-specific permissions to user."""
    provider_group, _ = Group.objects.get_or_create(name="master")
    user.groups.add(provider_group)
    permissions = Permission.objects.filter(
        codename__in=["view_job", "add_bid", "view_bid", "change_bid", "view_payment"]
    )
    for perm in permissions:
        user.user_permissions.add(perm)

    MasterStatistics.objects.create(master=user.master_profile)


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
        """Create master profile."""

        response = super().create(request, *args, **kwargs)
        assign_master_permissions(request.user)
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
        qs = provider_profile.master_skills.prefetch_related("skill")
        return qs


class MasterPortfolioAPIViewSet(ModelViewSet):
    """Crud for service master portfolio items."""

    serializer_class = PortfolioItemSerializer
    permission_classes = [IsAuthenticated, HasMasterProfile]

    def get_queryset(self):
        provider_profile = self.request.user.master_profile
        return provider_profile.portfolio_items.select_related("skill_used").prefetch_related("attachments")

    def perform_destroy(self, instance: PortfolioItem):
        instance.attachments.all().delete()
        instance.delete()


class MasterPortfolioAttachmentAPIViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated, IsAttachmentOwner, HasMasterProfile]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def _get_portfolio_obj(self) -> PortfolioItem:
        if hasattr(self.request, "_portfolio_obj"):
            return self.request._portfolio_obj
        parent_lookup_field = "portfolio_id"
        portfolio_id = self.kwargs.get(parent_lookup_field)
        item: PortfolioItem = get_object_or_404(PortfolioItem, id=portfolio_id)
        if item.master != self.request.user.master_profile:
            raise PermissionDenied("You are not the owner of this job assignment")
        self.request._portfolio_obj = item
        return self.request._portfolio_obj

    def get_queryset(self):
        item = self._get_portfolio_obj()
        return item.attachments.all()

    def get_serializer_class(self):
        if self.action == "create":
            return PortfolioItemAttachmentUploadSerializer
        return AttachmentSerializer

    def perform_create(self, serializer):
        item = self._get_portfolio_obj()
        files = serializer.validated_data["files"]
        if not files:
            raise ValidationError("No files provided")
        attachments = create_attachments(files, self.request.user, item)
        for a in attachments:
            item.attachments.add(a)
        return attachments


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
        return Master.objects.select_related(
            'user',
            'profession',
            'statistics'
        ).prefetch_related(
            'skills',
            'portfolio_items',
            'certificates',
        ).filter(user__is_active=True)

    @extend_schema(
        description="Master Profile Details",
        responses={200: PublicMasterProfileDetailSerializer},
        operation_id="v1_users_masters_details"
    )
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        obj = self.get_object()
        return Response(PublicMasterProfileDetailSerializer(instance=obj).data)


class MasterUpdateOnlineStatusAPIView(APIView):
    """Update online status for master."""

    permission_classes = [IsAuthenticated, HasMasterProfile]

    @extend_schema(
        description="Update online status for master",
        request=MasterOnlineStatusRequestSerializer,
        responses={
            200: MasterOnlineStatusResponseSerializer,
        },
        operation_id="v1_users_masters_update_online_status"
    )
    def post(self, request):
        """Update online status for master."""

        # Validate request data using serializer
        serializer = MasterOnlineStatusRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        is_online = serializer.validated_data['is_online']

        # Update master profile
        provider_profile: Master = request.user.master_profile
        provider_profile.is_online = is_online
        provider_profile.last_seen = timezone.now()
        provider_profile.save(update_fields=['is_online', 'last_seen'])

        return Response({
            'message': 'Online status updated successfully',
            'is_online': is_online,
            'last_seen': provider_profile.last_seen
        }, status=status.HTTP_200_OK)
