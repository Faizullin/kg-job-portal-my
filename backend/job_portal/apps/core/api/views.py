from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from utils.exceptions import StandardizedViewMixin
from utils.permissions import HasSpecificPermission
from utils.pagination import CustomPagination
from ..models import Language, ServiceCategory, ServiceSubcategory, ServiceArea, SystemSettings, SupportFAQ
from .serializers import (
    LanguageSerializer, ServiceCategorySerializer, ServiceSubcategorySerializer,
    ServiceAreaSerializer, SystemSettingsSerializer, SupportFAQSerializer, 
    ServiceCategoryCreateUpdateSerializer, ServiceSubcategoryCreateUpdateSerializer, 
    ServiceAreaCreateUpdateSerializer, SystemSettingsCreateUpdateSerializer,
    SupportFAQCreateUpdateSerializer
)


# Unified ViewSets - Single class per model with all functionality
class LanguageViewSet(StandardizedViewMixin, viewsets.ReadOnlyModelViewSet):
    """Languages - Read-only (managed via admin/fixtures)."""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_default']
    search_fields = ['code', 'name', 'native_name']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    pagination_class = CustomPagination


class ServiceCategoryViewSet(StandardizedViewMixin, viewsets.ModelViewSet):
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
            return [HasSpecificPermission(['core.add_servicecategory', 'core.change_servicecategory', 'core.delete_servicecategory'])]


class ServiceSubcategoryViewSet(StandardizedViewMixin, viewsets.ModelViewSet):
    """Service Subcategories - Full CRUD with authenticated access."""
    queryset = ServiceSubcategory.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active', 'featured']
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
            return [HasSpecificPermission(['core.add_servicesubcategory', 'core.change_servicesubcategory', 'core.delete_servicesubcategory'])]


class ServiceAreaViewSet(StandardizedViewMixin, viewsets.ModelViewSet):
    """Service Areas - Full CRUD with authenticated access."""
    queryset = ServiceArea.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
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
            return [HasSpecificPermission(['core.add_servicearea', 'core.change_servicearea', 'core.delete_servicearea'])]


class SystemSettingsViewSet(StandardizedViewMixin, viewsets.ModelViewSet):
    """System Settings - Full CRUD with admin access."""
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
            return [HasSpecificPermission(['core.add_systemsettings', 'core.change_systemsettings', 'core.delete_systemsettings'])]


class SupportFAQViewSet(StandardizedViewMixin, viewsets.ModelViewSet):
    """Support FAQ - Full CRUD with admin access."""
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
            return [HasSpecificPermission(['core.add_supportfaq', 'core.change_supportfaq', 'core.delete_supportfaq'])]