from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from utils.pagination import CustomPagination
from utils.permissions import HasSpecificPermission
from .serializers import (
    LanguageSerializer, ServiceCategorySerializer, ServiceSubcategorySerializer,
    ServiceAreaSerializer, SystemSettingsSerializer, SupportFAQSerializer,
    ServiceCategoryCreateUpdateSerializer, ServiceSubcategoryCreateUpdateSerializer,
    ServiceAreaCreateUpdateSerializer, SystemSettingsCreateUpdateSerializer,
    SupportFAQCreateUpdateSerializer
)
from ..models import Language, ServiceCategory, ServiceSubcategory, ServiceArea, SystemSettings, SupportFAQ


class LanguageReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    """Languages - Read-only (managed via admin/fixtures)."""

    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "is_default": ["exact"],
        "is_active": ["exact"],
        "id": ["in"],
    }
    search_fields = ['code', 'name', 'native_name']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    pagination_class = CustomPagination


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """Service Categories - Full CRUD with authenticated access."""

    queryset = ServiceCategory.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'featured']
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ServiceCategorySerializer
        else:
            return ServiceCategoryCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [HasSpecificPermission(
                ['core.add_servicecategory', 'core.change_servicecategory', 'core.delete_servicecategory'])]


class ServiceSubcategoryViewSet(viewsets.ModelViewSet):
    """Service Subcategories - Full CRUD with authenticated access."""

    queryset = ServiceSubcategory.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'category': ["exact"],
        'featured': ["exact"],
        "is_active": ["exact"],
        'id': ['in'],
    }
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ServiceSubcategorySerializer
        else:
            return ServiceSubcategoryCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [HasSpecificPermission(
                ['core.add_servicesubcategory', 'core.change_servicesubcategory', 'core.delete_servicesubcategory'])]


class ServiceAreaViewSet(viewsets.ModelViewSet):
    """Service Areas - Full CRUD with authenticated access."""

    queryset = ServiceArea.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "is_active": ["exact"],
        'id': ['in'],
    }
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ServiceAreaSerializer
        else:
            return ServiceAreaCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [
                HasSpecificPermission(['core.add_servicearea', 'core.change_servicearea', 'core.delete_servicearea'])()]


class SystemSettingsViewSet(viewsets.ModelViewSet):
    """System Settings - Full CRUD with authenticated access."""

    queryset = SystemSettings.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['key', 'description']
    ordering_fields = ['key', 'category', 'created_at']
    ordering = ['category', 'key']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return SystemSettingsSerializer
        else:
            return SystemSettingsCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [HasSpecificPermission(
                ['core.add_systemsettings', 'core.change_systemsettings', 'core.delete_systemsettings'])]


class SupportFAQViewSet(viewsets.ModelViewSet):
    """Support FAQs - Full CRUD with authenticated access."""

    queryset = SupportFAQ.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active', 'language']
    search_fields = ['question', 'answer']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order', 'question']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return SupportFAQSerializer
        else:
            return SupportFAQCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [HasSpecificPermission(['core.add_supportfaq', 'core.change_supportfaq', 'core.delete_supportfaq'])()]
