from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404

from utils.crud_base.views import AbstractBaseListApiView, AbstractBaseApiView
from utils.permissions import AbstractIsAuthenticatedOrReadOnly, AbstractHasSpecificPermission
from ..models import UserProfile, ServiceProviderProfile, ClientProfile, UserVerification, ServiceProviderService
from .serializers import (
    UserProfileSerializer, ServiceProviderSerializer, ClientSerializer,
    UserProfileUpdateSerializer, ServiceProviderUpdateSerializer, ClientUpdateSerializer
)


class UserProfileApiView(AbstractBaseListApiView):
    serializer_class = UserProfileSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['user_type', 'is_verified', 'gender']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone', 'address']
    ordering_fields = ['rating', 'total_reviews', 'created_at']
    ordering = ['-rating', '-total_reviews']
    
    def get_queryset(self):
        return UserProfile.objects.filter(is_deleted=False).select_related('user', 'service_provider_profile', 'client_profile')
    
    @action(detail=False, methods=['get'])
    def service_providers(self, request):
        """Get all service providers with filtering."""
        providers = ServiceProviderProfile.objects.filter(
            user_profile__is_deleted=False,
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
        clients = ClientProfile.objects.filter(
            user_profile__is_deleted=False,
            user_profile__user_type='client'
        ).select_related('user_profile__user')
        
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)


class UserProfileDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user, is_deleted=False)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileSerializer
        return UserProfileUpdateSerializer


class ServiceProviderApiView(AbstractBaseListApiView):
    serializer_class = ServiceProviderSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['is_verified_provider', 'is_available']
    search_fields = ['business_name', 'user_profile__user__first_name', 'user_profile__user__last_name']
    ordering_fields = ['average_rating', 'years_of_experience', 'total_reviews']
    ordering = ['-average_rating', '-total_reviews']
    
    def get_queryset(self):
        return ServiceProviderProfile.objects.filter(
            user_profile__is_deleted=False
        ).select_related('user_profile__user')


class ServiceProviderDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ServiceProviderUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_object(self):
        return get_object_or_404(
            ServiceProviderProfile, 
            user_profile__user=self.request.user, 
            user_profile__is_deleted=False
        )
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceProviderSerializer
        return ServiceProviderUpdateSerializer


class ClientApiView(AbstractBaseListApiView):
    serializer_class = ClientSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['created_at']
    search_fields = ['user_profile__user__first_name', 'user_profile__user__last_name']
    ordering_fields = ['total_orders', 'created_at']
    ordering = ['-total_orders', '-created_at']
    
    def get_queryset(self):
        return ClientProfile.objects.filter(
            user_profile__is_deleted=False
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
