from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.crud_base.views import StandardizedViewMixin
from utils.pagination import CustomPagination

from ..models import ClientProfile, ServiceProviderProfile, UserProfile
from orders.models import Order
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
        return ClientProfile.objects.filter(
            user_profile__user_type='client'
        ).select_related('user_profile__user')


class ClientDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
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
class UserProfileUpdateView(StandardizedViewMixin, APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
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


class ClientProfileUpdateView(StandardizedViewMixin, APIView):
    permission_classes = [IsAuthenticated,]
    
    def post(self, request):
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


class ServiceProviderProfileUpdateView(StandardizedViewMixin, APIView):
    permission_classes = [IsAuthenticated, ]
    
    def post(self, request):
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


class AdvancedProfileApiView(StandardizedViewMixin, APIView):
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
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'service_date']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        """Get user's task history based on their role."""
        user = self.request.user
        try:
            if hasattr(user, 'job_portal_profile'):
                if user.job_portal_profile.user_type in ['client', 'both']:
                    # Client's created orders
                    return Order.objects.filter(
                        client__user_profile__user=user
                    ).select_related('service_subcategory', 'client__user_profile__user')
                elif user.job_portal_profile.user_type in ['service_provider', 'both']:
                    # Provider's assigned orders
                    return Order.objects.filter(
                        assignment__provider__user_profile__user=user
                    ).select_related('service_subcategory', 'assignment__provider__user_profile__user')
        except Exception:
            pass
        
        # Fallback: return empty queryset
        return Order.objects.none()
