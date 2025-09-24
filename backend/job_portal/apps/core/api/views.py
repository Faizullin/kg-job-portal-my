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
        elif self.action == 'create':
            return [IsAuthenticated(), HasSpecificPermission(['core.add_servicecategory'])()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), HasSpecificPermission(['core.change_servicecategory'])()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), HasSpecificPermission(['core.delete_servicecategory'])()]
        else:
            return [IsAuthenticated()]


class ServiceSubcategoryViewSet(StandardizedViewMixin, viewsets.ModelViewSet):
    """Service Subcategories - Full CRUD with authenticated access."""
    queryset = ServiceSubcategory.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'category', 'featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['category', 'sort_order']
    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ServiceSubcategorySerializer
        else:
            return ServiceSubcategoryCreateUpdateSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated(), HasSpecificPermission(['core.add_servicesubcategory'])()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), HasSpecificPermission(['core.change_servicesubcategory'])()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), HasSpecificPermission(['core.delete_servicesubcategory'])()]
        else:
            return [IsAuthenticated()]


class ServiceAreaViewSet(StandardizedViewMixin, viewsets.ModelViewSet):
    """Service Areas - Full CRUD with authenticated access."""
    queryset = ServiceArea.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'country', 'state']
    search_fields = ['name', 'city', 'state', 'country']
    ordering_fields = ['name', 'city', 'state', 'country', 'created_at']
    ordering = ['country', 'state', 'city']
    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ServiceAreaSerializer
        else:
            return ServiceAreaCreateUpdateSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated(), HasSpecificPermission(['core.add_servicearea'])()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), HasSpecificPermission(['core.change_servicearea'])()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), HasSpecificPermission(['core.delete_servicearea'])()]
        else:
            return [IsAuthenticated()]


class SystemSettingsViewSet(StandardizedViewMixin, viewsets.ModelViewSet):
    """System Settings - Admin-only CRUD."""
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_public', 'category']
    search_fields = ['key', 'description']
    ordering_fields = ['key', 'category', 'created_at']
    ordering = ['category', 'key']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return SystemSettings.objects.all()
        else:
            return SystemSettings.objects.filter(is_public=True)
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return SystemSettingsSerializer
        else:
            return SystemSettingsCreateUpdateSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated(), HasSpecificPermission(['core.add_systemsettings'])()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), HasSpecificPermission(['core.change_systemsettings'])()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), HasSpecificPermission(['core.delete_systemsettings'])()]
        else:
            return [IsAuthenticated()]


class SupportFAQViewSet(StandardizedViewMixin, viewsets.ModelViewSet):
    """Support FAQ - Authenticated read, Admin write."""
    queryset = SupportFAQ.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_popular', 'is_active']
    search_fields = ['question', 'answer']
    ordering_fields = ['sort_order', 'view_count', 'created_at']
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
        elif self.action == 'create':
            return [IsAuthenticated(), HasSpecificPermission(['core.add_supportfaq'])()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), HasSpecificPermission(['core.change_supportfaq'])()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), HasSpecificPermission(['core.delete_supportfaq'])()]
        else:
            return [IsAuthenticated()]


