from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.exceptions import StandardizedViewMixin
from utils.pagination import CustomPagination

from ..models import ClientProfile, ServiceProviderProfile, UserProfile
from job_portal.apps.orders.models import Order
from job_portal.apps.orders.api.serializers import OrderSerializer
from .serializers import (
    ClientSerializer,
    ClientUpdateSerializer,
    ServiceProviderSerializer,
    ServiceProviderUpdateSerializer,
    UserProfileDetailSerializer,
    UserProfileUpdateSerializer,
    AdvancedProfileSerializer,
    AdvancedProfileUpdateSerializer,
)
from django.contrib.auth.models import Group, Permission
from utils.permissions import HasClientProfile, HasServiceProviderProfile


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


class ServiceProviderApiView(StandardizedViewMixin, generics.ListAPIView):
    """List all available service providers with search and filtering."""
    serializer_class = ServiceProviderSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_verified_provider']
    search_fields = ['business_name', 'user_profile__user__first_name', 'user_profile__user__last_name']
    ordering_fields = ['average_rating', 'total_reviews']
    ordering = ['-average_rating', '-total_reviews']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        """Always filter on available providers only."""
        return ServiceProviderProfile.objects.filter(
            is_available=True
        ).select_related('user_profile__user')


class ServiceProviderFeaturedApiView(StandardizedViewMixin, generics.ListAPIView):
    """Featured service providers for mobile app."""
    serializer_class = ServiceProviderSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_verified_provider', 'is_available']
    ordering_fields = ['average_rating', 'total_reviews']
    ordering = ['-average_rating', '-total_reviews']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        """Get featured providers (verified and highly rated)."""
        return ServiceProviderProfile.objects.filter(
            is_verified_provider=True,
            is_available=True,
            average_rating__gte=4.0
        ).select_related('user_profile__user')




class ServiceProviderDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = ServiceProviderUpdateSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    
    def get_object(self):
        return get_object_or_404(
            ServiceProviderProfile, 
            user_profile__user=self.request.user
        )
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceProviderSerializer
        return ServiceProviderUpdateSerializer


class ClientApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['user_profile__user__first_name', 'user_profile__user__last_name']
    ordering_fields = ['total_orders', 'created_at']
    ordering = ['-total_orders', '-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return ClientProfile.objects.all().select_related('user_profile__user')


class ClientDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = ClientUpdateSerializer
    permission_classes = [IsAuthenticated, HasClientProfile]
    
    def get_object(self):
        return get_object_or_404(
            ClientProfile, 
            user_profile__user=self.request.user
        )
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClientSerializer
        return ClientUpdateSerializer


# Profile Creation Views
# Simple Profile Update Views
class ClientProfileCreateView(StandardizedViewMixin, APIView):
    serializer_class = ClientUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
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
        
        serializer = ClientUpdateSerializer(data=request.data)
        if serializer.is_valid():
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
            user_profile.user_type = 'client'
            user_profile.save()
            
            return Response({
                'message': 'Client profile created successfully',
                'client_profile': ClientUpdateSerializer(client_profile).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientProfileUpdateView(StandardizedViewMixin, APIView):
    serializer_class = ClientUpdateSerializer
    permission_classes = [IsAuthenticated,]
    
    def post(self, request):
        serializer = ClientUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_profile = request.user.job_portal_profile
            
            # Extract many-to-many fields
            validated_data = serializer.validated_data.copy()
            preferred_services = validated_data.pop('preferred_services', None)
            
            client_profile, created = ClientProfile.objects.update_or_create(
                user_profile=user_profile,
                defaults=validated_data
            )
            
            # Set many-to-many fields if provided
            if preferred_services is not None:
                client_profile.preferred_services.set(preferred_services)
            
            return Response({
                'message': 'Client profile updated successfully',
                'client_profile': ClientUpdateSerializer(client_profile).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceProviderProfileCreateView(StandardizedViewMixin, APIView):
    serializer_class = ServiceProviderUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
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
        
        serializer = ServiceProviderUpdateSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data.copy()
            service_areas = validated_data.pop('service_areas', None)
            services_offered = validated_data.pop('services_offered', None)
            
            provider_profile = ServiceProviderProfile.objects.create(
                user_profile=user_profile,
                **validated_data
            )
            
            if service_areas is not None:
                provider_profile.service_areas.set(service_areas)
            if services_offered is not None:
                provider_profile.services_offered.set(services_offered)
            
            # Automatically assign service provider permissions
            assign_service_provider_permissions(request.user)
            
            # Update user type in profile
            user_profile.user_type = 'service_provider'
            user_profile.save()
            
            return Response({
                'message': 'Service provider profile created successfully',
                'provider_profile': ServiceProviderUpdateSerializer(provider_profile).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceProviderProfileUpdateView(StandardizedViewMixin, APIView):
    serializer_class = ServiceProviderUpdateSerializer
    permission_classes = [IsAuthenticated, ]
    
    def post(self, request):
        serializer = ServiceProviderUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_profile = request.user.job_portal_profile
            
            # Extract many-to-many fields
            validated_data = serializer.validated_data.copy()
            service_areas = validated_data.pop('service_areas', None)
            services_offered = validated_data.pop('services_offered', None)
            
            provider_profile, created = ServiceProviderProfile.objects.update_or_create(
                user_profile=user_profile,
                defaults=validated_data
            )
            
            # Set many-to-many fields if provided
            if service_areas is not None:
                provider_profile.service_areas.set(service_areas)
            if services_offered is not None:
                provider_profile.services_offered.set(services_offered)
            
            return Response({
                'message': 'Service provider profile updated successfully',
                'provider_profile': ServiceProviderUpdateSerializer(provider_profile).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdvancedProfileApiView(StandardizedViewMixin, APIView):
    serializer_class = AdvancedProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = AdvancedProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = AdvancedProfileUpdateSerializer(
            instance=request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            updated_user = serializer.save()
            response_serializer = AdvancedProfileSerializer(updated_user)
            return Response({
                'message': 'Profile updated successfully',
                'data': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskHistoryApiView(StandardizedViewMixin, generics.ListAPIView):
    """Task history for users (orders they created or worked on)."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'service_date']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        """Get user's task history based on their role."""
        user = self.request.user
        
        # Check if user has client profile
        if ClientProfile.objects.filter(user_profile__user=user).exists():
            # Client's created orders
            return Order.objects.filter(
                client__user_profile__user=user
            ).select_related('service_subcategory', 'client__user_profile')
        
        # Check if user has service provider profile
        if ServiceProviderProfile.objects.filter(user_profile__user=user).exists():
            # Provider's assigned orders
            return Order.objects.filter(
                assignment__provider__user_profile__user=user
            ).select_related('service_subcategory', 'assignment__provider__user_profile')
        
        # Fallback: return empty queryset
        return Order.objects.none()
