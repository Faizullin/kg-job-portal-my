from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.pagination import CustomPagination

from ..models import ClientProfile, ServiceProviderProfile, UserProfile
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


class UserProfileDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        # Simple filtering - manager automatically handles is_deleted
        return get_object_or_404(UserProfile, user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileDetailSerializer
        return UserProfileUpdateSerializer


class ServiceProviderApiView(generics.ListAPIView):
    serializer_class = ServiceProviderSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_verified_provider', 'is_available']
    search_fields = ['business_name', 'user_profile__user__first_name', 'user_profile__user__last_name']
    ordering_fields = ['average_rating', 'years_of_experience', 'total_reviews']
    ordering = ['-average_rating', '-total_reviews']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return ServiceProviderProfile.objects.all().select_related('user_profile__user')


class ServiceProviderDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ServiceProviderUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
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
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['user_profile__user__first_name', 'user_profile__user__last_name']
    ordering_fields = ['total_orders', 'created_at']
    ordering = ['-total_orders', '-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return ClientProfile.objects.filter(
            user_profile__user_type='client'
        ).select_related('user_profile__user')


class ClientDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientUpdateSerializer
    permission_classes = [IsAuthenticated]
    
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


class AdvancedProfileApiView(APIView):
    """Advanced profile API that combines user account data and job portal profile."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get combined user account and job portal profile data."""
        serializer = AdvancedProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Update both user account and job portal profile data."""
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
