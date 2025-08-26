from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from utils.crud_base.views import AbstractBaseListApiView, AbstractBaseApiView
from utils.permissions import AbstractIsAuthenticatedOrReadOnly, AbstractHasSpecificPermission
from ..models import Language, ServiceCategory, ServiceSubcategory, ServiceArea, SystemSettings, AppVersion
from .serializers import (
    LanguageSerializer, ServiceCategorySerializer, ServiceSubcategorySerializer,
    ServiceAreaSerializer, SystemSettingsSerializer, AppVersionSerializer
)


class LanguageApiView(AbstractBaseListApiView):
    serializer_class = LanguageSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['is_active', 'is_default']
    search_fields = ['code', 'name', 'native_name']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        return Language.objects.filter(is_deleted=False)


class ServiceCategoryApiView(AbstractBaseListApiView):
    serializer_class = ServiceCategorySerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['is_active', 'featured']
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self):
        return ServiceCategory.objects.filter(is_deleted=False)


class ServiceSubcategoryApiView(AbstractBaseListApiView):
    serializer_class = ServiceSubcategorySerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['is_active', 'category', 'featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['category', 'sort_order']
    
    def get_queryset(self):
        return ServiceSubcategory.objects.filter(is_deleted=False)


class ServiceAreaApiView(AbstractBaseListApiView):
    serializer_class = ServiceAreaSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['is_active', 'country', 'state']
    search_fields = ['name', 'city', 'state', 'country']
    ordering_fields = ['name', 'city', 'state', 'country', 'created_at']
    ordering = ['country', 'state', 'city']
    
    def get_queryset(self):
        return ServiceArea.objects.filter(is_deleted=False)


class SystemSettingsApiView(AbstractBaseListApiView):
    serializer_class = SystemSettingsSerializer
    permission_classes = [AbstractHasSpecificPermission(['core.view_systemsettings'])]
    filterset_fields = ['is_public', 'category']
    search_fields = ['key', 'description']
    ordering_fields = ['key', 'category', 'created_at']
    ordering = ['category', 'key']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return SystemSettings.objects.all()
        return SystemSettings.objects.filter(is_public=True)


class AppVersionApiView(AbstractBaseListApiView):
    serializer_class = AppVersionSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['is_active', 'platform']
    search_fields = ['version', 'release_notes']
    ordering_fields = ['version', 'build_number', 'release_date', 'created_at']
    ordering = ['-build_number']
    
    def get_queryset(self):
        return AppVersion.objects.all()
