from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
# from django.db.models import Q

from utils.permissions import AbstractIsAuthenticatedOrReadOnly, HasSpecificPermission
from utils.pagination import CustomPagination
from ..models import Language, ServiceCategory, ServiceSubcategory, ServiceArea, SystemSettings, AppVersion
from .serializers import (
    LanguageSerializer, ServiceCategorySerializer, ServiceSubcategorySerializer,
    ServiceAreaSerializer, SystemSettingsSerializer, AppVersionSerializer
)


class LanguageApiView(generics.ListAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_default']
    search_fields = ['code', 'name', 'native_name']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        return Language.objects.all()


class ServiceCategoryApiView(generics.ListAPIView):
    serializer_class = ServiceCategorySerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'featured']
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        return ServiceCategory.objects.all()


class ServiceSubcategoryApiView(generics.ListAPIView):
    serializer_class = ServiceSubcategorySerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'category', 'featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['category', 'sort_order']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        return ServiceSubcategory.objects.all()


class ServiceAreaApiView(generics.ListAPIView):
    serializer_class = ServiceAreaSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'country', 'state']
    search_fields = ['name', 'city', 'state', 'country']
    ordering_fields = ['name', 'city', 'state', 'country', 'created_at']
    ordering = ['country', 'state', 'city']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        return ServiceArea.objects.all()


class SystemSettingsApiView(generics.ListAPIView):
    serializer_class = SystemSettingsSerializer
    permission_classes = [HasSpecificPermission(['core.add_systemsettings'])]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_public', 'category']
    search_fields = ['key', 'description']
    ordering_fields = ['key', 'category', 'created_at']
    ordering = ['category', 'key']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return SystemSettings.objects.all()
        # Simple filtering - manager automatically handles is_deleted
        return SystemSettings.objects.filter(is_public=True)


class AppVersionApiView(generics.ListAPIView):
    serializer_class = AppVersionSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'platform']
    search_fields = ['version', 'release_notes']
    ordering_fields = ['version', 'build_number', 'release_date', 'created_at']
    ordering = ['-build_number']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return AppVersion.objects.all()
