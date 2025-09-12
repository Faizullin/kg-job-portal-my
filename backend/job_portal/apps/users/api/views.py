from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from utils.permissions import AbstractIsAuthenticatedOrReadOnly, HasClientProfile, HasServiceProviderProfile
from utils.pagination import CustomPagination
from ..models import UserProfile, ServiceProviderProfile, ClientProfile, UserVerification, ServiceProviderService
from .serializers import (
    UserProfileDetailSerializer, ServiceProviderSerializer, ClientSerializer,
    UserProfileUpdateSerializer, ServiceProviderUpdateSerializer, ClientUpdateSerializer,
)


class UserProfileApiView(generics.ListAPIView):
    serializer_class = UserProfileDetailSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_type', 'is_verified', 'gender']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone', 'address']
    ordering_fields = ['rating', 'total_reviews', 'created_at']
    ordering = ['-rating', '-total_reviews']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        return UserProfile.objects.all().select_related('user', 'service_provider_profile', 'client_profile')
    
    @action(detail=False, methods=['get'])
    def service_providers(self, request):
        """Get all service providers with filtering."""
        # Simple filtering - manager automatically handles is_deleted
        providers = ServiceProviderProfile.objects.filter(
            user_profile__user_type='service_provider'
        ).select_related('user_profile__user')
        
        # Apply filters
        business_name = request.query_params.get('business_name')
        if business_name:
            providers = providers.filter(business_name__icontains=business_name)
        
        min_rating = request.query_params.get('min_rating')
        if min_rating:
            providers = providers.filter(average_rating__gte=float(min_rating))
        
        min_experience = request.query_params.get('min_experience')
        if min_experience:
            providers = providers.filter(years_of_experience__gte=int(min_experience))
        
        serializer = ServiceProviderSerializer(providers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def clients(self, request):
        """Get all clients with filtering."""
        # Simple filtering - manager automatically handles is_deleted
        clients = ClientProfile.objects.filter(
            user_profile__user_type='client'
        ).select_related('user_profile__user')
        
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)


class UserProfileDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_object(self):
        # Simple filtering - manager automatically handles is_deleted
        return get_object_or_404(UserProfile, user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileDetailSerializer
        return UserProfileUpdateSerializer


class ServiceProviderApiView(generics.ListAPIView):
    serializer_class = ServiceProviderSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_verified_provider', 'is_available']
    search_fields = ['business_name', 'user_profile__user__first_name', 'user_profile__user__last_name']
    ordering_fields = ['average_rating', 'years_of_experience', 'total_reviews']
    ordering = ['-average_rating', '-total_reviews']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        return ServiceProviderProfile.objects.all().select_related('user_profile__user')


class ServiceProviderDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ServiceProviderUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_object(self):
        # Simple filtering - manager automatically handles is_deleted
        return get_object_or_404(
            ServiceProviderProfile, 
            user_profile__user=self.request.user
        )
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceProviderSerializer
        return ServiceProviderUpdateSerializer


class ClientApiView(generics.ListAPIView):
    serializer_class = ClientSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['user_profile__user__first_name', 'user_profile__user__last_name']
    ordering_fields = ['total_orders', 'created_at']
    ordering = ['-total_orders', '-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # Simple filtering - manager automatically handles is_deleted
        return ClientProfile.objects.filter(
            user_profile__user_type='client'
        ).select_related('user_profile__user')


class ClientDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_object(self):
        return get_object_or_404(
            ClientProfile, 
            user_profile__user=self.request.user, 
            user_profile__is_deleted=False
        )
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClientSerializer
        return ClientUpdateSerializer


# Simple Profile Update Views
class UserProfileUpdateView(APIView):
    """Update user profile - works for both registration and profile updates"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create or update user profile"""
        serializer = UserProfileUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_profile, created = UserProfile.objects.update_or_create(
                user=request.user,
                defaults=serializer.validated_data
            )
            return Response({
                'message': 'Profile updated successfully',
                'profile': UserProfileUpdateSerializer(user_profile).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientProfileUpdateView(APIView):
    """Update client profile - works for both registration and profile updates"""
    permission_classes = [IsAuthenticated,]
    
    def post(self, request):
        """Create or update client profile"""
        serializer = ClientUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_profile = request.user.job_portal_profile
            client_profile, created = ClientProfile.objects.update_or_create(
                user_profile=user_profile,
                defaults=serializer.validated_data
            )
            return Response({
                'message': 'Client profile updated successfully',
                'client_profile': ClientUpdateSerializer(client_profile).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceProviderProfileUpdateView(APIView):
    """Update service provider profile - works for both registration and profile updates"""
    permission_classes = [IsAuthenticated, ]
    
    def post(self, request):
        """Create or update service provider profile"""
        serializer = ServiceProviderUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_profile = request.user.job_portal_profile
            provider_profile, created = ServiceProviderProfile.objects.update_or_create(
                user_profile=user_profile,
                defaults=serializer.validated_data
            )
            return Response({
                'message': 'Service provider profile updated successfully',
                'provider_profile': ServiceProviderUpdateSerializer(provider_profile).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
