from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from utils.exceptions import StandardizedViewMixin

from ..models import (
    ClientProfile, ServiceProviderProfile, UserProfile, 
    MasterSkill, ServiceProviderSkill, PortfolioItem, Certificate,
    Profession, ProviderStatistics
)
from .serializers import (
    ClientUpdateSerializer,
    ServiceProviderUpdateSerializer,
    UserProfileDetailSerializer,
    UserProfileUpdateSerializer,
    AdvancedProfileSerializer,
    AdvancedProfileUpdateSerializer,
    MasterSkillSerializer,
    ServiceProviderSkillSerializer,
    PortfolioItemSerializer,
    CertificateSerializer,
    ProfessionSerializer,
    ProviderStatisticsSerializer,
    ServiceProviderDetailSerializer,
)
from django.contrib.auth.models import Group, Permission
from utils.permissions import HasServiceProviderProfile


def assign_client_permissions(user):
    """Assign client-specific permissions to user."""
    client_group, created = Group.objects.get_or_create(name='client')
    user.groups.add(client_group)
    
    # Assign basic client permissions
    permissions = Permission.objects.filter(
        codename__in=['add_order', 'view_order', 'change_order', 'view_bid', 'add_payment', 'view_payment']
    )
    for perm in permissions:
        user.user_permissions.add(perm)


def assign_service_provider_permissions(user):
    """Assign service provider-specific permissions to user."""
    provider_group, created = Group.objects.get_or_create(name='service_provider')
    user.groups.add(provider_group)
    
    # Assign basic service provider permissions
    permissions = Permission.objects.filter(
        codename__in=['view_order', 'add_bid', 'view_bid', 'change_bid', 'view_payment']
    )
    for perm in permissions:
        user.user_permissions.add(perm)


class UserProfileDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileDetailSerializer
        return UserProfileUpdateSerializer








class ServiceProviderDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = ServiceProviderDetailSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get provider with all related data."""
        return ServiceProviderProfile.objects.select_related(
            'user_profile__user', 
            'statistics',
            'profession__category'
        ).prefetch_related(
            'provider_skills__skill',
            'portfolio_items',
            'certificates'
        )
    
    def get_object(self):
        """Get provider by ID and ensure related models are initialized."""
        provider = get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs['pk']
        )
        # Ensure all related models are initialized
        provider.initialize_related_models()
        return provider
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceProviderDetailSerializer
        return ServiceProviderUpdateSerializer




# Profile Creation Views
class ClientProfileViewSet(StandardizedViewMixin, generics.GenericAPIView):
    """Client profile viewset with create, retrieve, update, and partial_update methods."""
    serializer_class = ClientUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get client profile for authenticated user."""
        try:
            return ClientProfile.objects.get(user_profile__user=self.request.user)
        except ClientProfile.DoesNotExist:
            return None
    
    def create(self, request, *args, **kwargs):
        """Create client profile."""
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User must have a job portal profile first'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if ClientProfile.objects.filter(user_profile=user_profile).exists():
            return Response({
                'error': 'User already has a client profile'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data.copy()
        preferred_services = validated_data.pop('preferred_services', None)
        
        client_profile = ClientProfile.objects.create(
            user_profile=user_profile,
            **validated_data
        )
        
        if preferred_services is not None:
            client_profile.preferred_services.set(preferred_services)
        
        # Automatically assign client permissions
        assign_client_permissions(request.user)
        
        # Update user type in profile
        user_profile.save()
        
        return Response({
            'message': 'Client profile created successfully',
            'client_profile': ClientUpdateSerializer(client_profile).data
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve client profile."""
        instance = self.get_object()
        if not instance:
            return Response({
                'error': 'Client profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({
            'client_profile': serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """Update client profile (full update)."""
        instance = self.get_object()
        if not instance:
            return Response({
                'error': 'Client profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        
        # Extract many-to-many fields
        validated_data = serializer.validated_data.copy()
        preferred_services = validated_data.pop('preferred_services', None)
        
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Set many-to-many fields if provided
        if preferred_services is not None:
            instance.preferred_services.set(preferred_services)
        
        return Response({
            'message': 'Client profile updated successfully',
            'client_profile': ClientUpdateSerializer(instance).data
        }, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        """Update client profile (partial update)."""
        instance = self.get_object()
        if not instance:
            return Response({
                'error': 'Client profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Extract many-to-many fields
        validated_data = serializer.validated_data.copy()
        preferred_services = validated_data.pop('preferred_services', None)
        
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Set many-to-many fields if provided
        if preferred_services is not None:
            instance.preferred_services.set(preferred_services)
        
        return Response({
            'message': 'Client profile updated successfully',
            'client_profile': ClientUpdateSerializer(instance).data
        }, status=status.HTTP_200_OK)


class ServiceProviderProfileRetrieveView(StandardizedViewMixin, generics.RetrieveAPIView):
    """Retrieve service provider profile for authenticated user."""
    serializer_class = ServiceProviderUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get service provider profile for authenticated user."""
        try:
            return ServiceProviderProfile.objects.get(user_profile__user=self.request.user)
        except ServiceProviderProfile.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve service provider profile."""
        instance = self.get_object()
        if not instance:
            return Response({
                'error': 'Service provider profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({
            'provider_profile': serializer.data
        }, status=status.HTTP_200_OK)


class ServiceProviderProfileCreateView(StandardizedViewMixin, generics.CreateAPIView):
    """Create service provider profile for authenticated user."""
    serializer_class = ServiceProviderUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create service provider profile."""
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User must have a job portal profile first'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if ServiceProviderProfile.objects.filter(user_profile=user_profile).exists():
            return Response({
                'error': 'User already has a service provider profile'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data.copy()
        service_areas = validated_data.pop('service_areas', None)
        services_offered = validated_data.pop('services_offered', None)
        
        # Create service provider profile
        provider_profile = ServiceProviderProfile.objects.create(
            user_profile=user_profile,
            **validated_data
        )
        
        # Set many-to-many relationships
        if service_areas is not None:
            provider_profile.service_areas.set(service_areas)
        if services_offered is not None:
            provider_profile.services_offered.set(services_offered)
        
        # Initialize all related models
        provider_profile.initialize_related_models()
        
        # Automatically assign service provider permissions
        assign_service_provider_permissions(request.user)
        
        return Response({
            'message': 'Service provider profile created successfully with initialized statistics',
            'provider_profile': ServiceProviderUpdateSerializer(provider_profile).data
        }, status=status.HTTP_201_CREATED)


class ServiceProviderProfileUpdateView(StandardizedViewMixin, generics.UpdateAPIView):
    """Update service provider profile for authenticated user."""
    serializer_class = ServiceProviderUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get service provider profile for authenticated user."""
        try:
            return ServiceProviderProfile.objects.get(user_profile__user=self.request.user)
        except ServiceProviderProfile.DoesNotExist:
            return None
    
    def update(self, request, *args, **kwargs):
        """Update service provider profile."""
        instance = self.get_object()
        if not instance:
            return Response({
                'error': 'Service provider profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Extract many-to-many fields
        validated_data = serializer.validated_data.copy()
        service_areas = validated_data.pop('service_areas', None)
        services_offered = validated_data.pop('services_offered', None)
        
        # Update existing profile
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        
        # Set many-to-many fields if provided
        if service_areas is not None:
            instance.service_areas.set(service_areas)
        if services_offered is not None:
            instance.services_offered.set(services_offered)
        
        return Response({
            'message': 'Service provider profile updated successfully',
            'provider_profile': ServiceProviderUpdateSerializer(instance).data
        }, status=status.HTTP_200_OK)


class AdvancedProfileApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = AdvancedProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdvancedProfileSerializer
        return AdvancedProfileUpdateSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_user = serializer.save()
        response_serializer = AdvancedProfileSerializer(updated_user)
        return Response({
            'message': 'Profile updated successfully',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)




# Mobile App Specific Views






class MasterSkillListApiView(StandardizedViewMixin, generics.ListAPIView):
    """List available skills for service providers."""
    serializer_class = MasterSkillSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        return MasterSkill.objects.filter(is_active=True).select_related('category')


class ServiceProviderSkillApiView(StandardizedViewMixin, generics.ListCreateAPIView):
    """Manage my service provider skills."""
    serializer_class = ServiceProviderSkillSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_primary_skill', 'proficiency_level']
    ordering_fields = ['is_primary_skill', 'years_of_experience']
    ordering = ['-is_primary_skill', '-years_of_experience']
    
    def get_queryset(self):
        """Get skills for current user's service provider profile."""
        try:
            provider_profile = ServiceProviderProfile.objects.get(
                user_profile__user=self.request.user
            )
            return ServiceProviderSkill.objects.filter(
                service_provider=provider_profile
            ).select_related('skill')
        except ServiceProviderProfile.DoesNotExist:
            return ServiceProviderSkill.objects.none()
    
    def perform_create(self, serializer):
        """Create skill for current user's provider profile."""
        provider_profile = ServiceProviderProfile.objects.get(
            user_profile__user=self.request.user
        )
        serializer.save(service_provider=provider_profile)


class PortfolioItemApiView(StandardizedViewMixin, generics.ListCreateAPIView):
    """Manage my service provider portfolio items."""
    serializer_class = PortfolioItemSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_featured', 'skill_used']
    ordering_fields = ['is_featured', 'created_at']
    ordering = ['-is_featured', '-created_at']
    
    def get_queryset(self):
        """Get portfolio items for current user's service provider profile."""
        try:
            provider_profile = ServiceProviderProfile.objects.get(
                user_profile__user=self.request.user
            )
            return PortfolioItem.objects.filter(
                service_provider=provider_profile
            ).select_related('skill_used')
        except ServiceProviderProfile.DoesNotExist:
            return PortfolioItem.objects.none()
    
    def perform_create(self, serializer):
        """Create portfolio item for current user's provider profile."""
        provider_profile = ServiceProviderProfile.objects.get(
            user_profile__user=self.request.user
        )
        serializer.save(service_provider=provider_profile)


class CertificateApiView(StandardizedViewMixin, generics.ListCreateAPIView):
    """Manage my service provider certificates."""
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_verified']
    ordering_fields = ['is_verified', 'issue_date']
    ordering = ['-is_verified', '-issue_date']
    
    def get_queryset(self):
        """Get certificates for current user's service provider profile."""
        try:
            provider_profile = ServiceProviderProfile.objects.get(
                user_profile__user=self.request.user
            )
            return Certificate.objects.filter(
                service_provider=provider_profile
            )
        except ServiceProviderProfile.DoesNotExist:
            return Certificate.objects.none()
    
    def perform_create(self, serializer):
        """Create certificate for current user's provider profile."""
        provider_profile = ServiceProviderProfile.objects.get(
            user_profile__user=self.request.user
        )
        serializer.save(service_provider=provider_profile)






class ProfessionListApiView(StandardizedViewMixin, generics.ListAPIView):
    """List available professions."""
    serializer_class = ProfessionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        return Profession.objects.filter(is_active=True).select_related('category')


class ProviderStatisticsApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    """Manage my provider statistics."""
    serializer_class = ProviderStatisticsSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    
    def get_object(self):
        """Get statistics for current user's provider profile."""
        provider_profile = ServiceProviderProfile.objects.get(
            user_profile__user=self.request.user
        )
        statistics, created = ProviderStatistics.objects.get_or_create(
            provider=provider_profile
        )
        return statistics
