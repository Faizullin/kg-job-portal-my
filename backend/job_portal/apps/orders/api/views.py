from utils.exceptions import StandardizedViewMixin
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from utils.permissions import HasSpecificPermission, HasClientProfile, HasServiceProviderProfile
from utils.pagination import CustomPagination
from ..models import Order, OrderAddon, OrderPhoto, Bid, OrderDispute
from job_portal.apps.users.models import ClientProfile, ServiceProviderProfile
from .serializers import (
    OrderSerializer, OrderAddonSerializer, OrderPhotoSerializer,
    BidSerializer, OrderDisputeSerializer, OrderCreateSerializer,
    OrderUpdateSerializer, BidCreateSerializer, OrderDisputeCreateSerializer, OrderDisputeUpdateSerializer
)


class OrderApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, HasClientProfile]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'service_subcategory', 'urgency']
    search_fields = ['title', 'description', 'location', 'city', 'state']
    ordering_fields = ['created_at', 'service_date', 'budget_min', 'budget_max']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            client__user_profile__user=user
        ).select_related('client__user_profile__user', 'service_subcategory')
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Get orders where user is the client."""
        orders = Order.objects.filter(
            client__user_profile__user=request.user,
            
        ).select_related('service_subcategory')
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailApiView(StandardizedViewMixin,generics.RetrieveUpdateAPIView):
    serializer_class = OrderUpdateSerializer
    permission_classes = [IsAuthenticated, HasSpecificPermission(['orders.view_order', 'orders.change_order'])]
    
    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            client__user_profile__user=user,
        ).select_related('client__user_profile__user', 'service_subcategory')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        return OrderUpdateSerializer


class OrderCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated, HasClientProfile, HasSpecificPermission(['orders.add_order'])]
    
    def perform_create(self, serializer):
        # Django automatically caches the profile when accessed
        client_profile = self.request.user.job_portal_profile.client_profile
        serializer.save(client=client_profile)


class OrderAddonApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = OrderAddonSerializer
    permission_classes = [IsAuthenticated, HasSpecificPermission(['orders.view_orderaddon'])]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['order']
    search_fields = ['addon__name']
    ordering_fields = ['quantity', 'price', 'created_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        return OrderAddon.objects.filter(
            order__,
            order__client__user_profile__user=user
        ).select_related('order', 'addon')


class OrderPhotoApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = OrderPhotoSerializer
    permission_classes = [IsAuthenticated, HasSpecificPermission(['orders.view_orderphoto'])]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['order', 'is_primary']
    ordering_fields = ['is_primary', 'created_at']
    ordering = ['-is_primary', '-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        return OrderPhoto.objects.filter(
            order__,
            order__client__user_profile__user=user
        ).select_related('order')


class BidApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, HasSpecificPermission(['orders.view_bid'])]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'order', 'is_negotiable']
    ordering_fields = ['amount', 'created_at']
    ordering = ['amount', '-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        return Bid.objects.filter(
            order__,
            order__client__user_profile__user=user
        ).select_related('order', 'provider__user_profile__user')


class BidCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = BidCreateSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile, HasSpecificPermission(['orders.add_bid'])]
    
    def perform_create(self, serializer):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id, )
        # Django automatically caches the profile when accessed
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        serializer.save(order=order, provider=provider_profile)


class OrderDisputeApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = OrderDisputeSerializer
    permission_classes = [IsAuthenticated, HasSpecificPermission(['orders.view_orderdispute'])]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['dispute_type', 'status', 'order']
    search_fields = ['description', 'admin_notes']
    ordering_fields = ['dispute_type', 'status', 'created_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        return OrderDispute.objects.filter(
            order__,
            order__client__user_profile__user=user
        ).select_related('order')


class OrderDisputeCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = OrderDisputeCreateSerializer
    permission_classes = [IsAuthenticated, HasClientProfile, HasSpecificPermission(['orders.add_orderdispute'])]
    
    def perform_create(self, serializer):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id, )
        serializer.save(order=order)


class OrderDisputeDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = OrderDisputeUpdateSerializer
    permission_classes = [IsAuthenticated, HasSpecificPermission(['orders.view_orderdispute', 'orders.change_orderdispute'])]
    
    def get_queryset(self):
        user = self.request.user
        return OrderDispute.objects.filter(
            order__,
            order__client__user_profile__user=user
        ).select_related('order')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderDisputeSerializer
        return OrderDisputeUpdateSerializer
