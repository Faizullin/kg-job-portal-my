from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404

from utils.crud_base.views import AbstractBaseListApiView, AbstractBaseApiView
from utils.permissions import AbstractIsAuthenticatedOrReadOnly, AbstractHasSpecificPermission
from ..models import Order, OrderAddon, OrderPhoto, Bid, OrderAssignment, OrderDispute
from .serializers import (
    OrderSerializer, OrderAddonSerializer, OrderPhotoSerializer,
    BidSerializer, OrderDisputeSerializer, OrderCreateSerializer,
    OrderUpdateSerializer, OrderAddonCreateSerializer, OrderAddonUpdateSerializer,
    BidCreateSerializer, BidUpdateSerializer, OrderDisputeCreateSerializer, OrderDisputeUpdateSerializer
)


class OrderApiView(AbstractBaseListApiView):
    serializer_class = OrderSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['status', 'service_subcategory', 'urgency']
    search_fields = ['title', 'description', 'location', 'city', 'state']
    ordering_fields = ['created_at', 'service_date', 'budget_min', 'budget_max']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        # Users can see orders they're involved in (as client)
        return Order.objects.filter(
            client__user_profile__user=user,
            is_deleted=False
        ).select_related('client__user_profile__user', 'service_subcategory')
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Get orders where user is the client."""
        orders = Order.objects.filter(
            client__user_profile__user=request.user,
            is_deleted=False
        ).select_related('service_subcategory')
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            client__user_profile__user=user,
            is_deleted=False
        ).select_related('client__user_profile__user', 'service_subcategory')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        return OrderUpdateSerializer


class OrderCreateApiView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        # Set the client to the current user
        client_profile = get_object_or_404(
            'users.ClientProfile', 
            user_profile__user=self.request.user
        )
        serializer.save(client=client_profile)


class OrderAddonApiView(AbstractBaseListApiView):
    serializer_class = OrderAddonSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['order']
    search_fields = ['addon__name']
    ordering_fields = ['quantity', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return OrderAddon.objects.filter(
            order__is_deleted=False,
            order__client__user_profile__user=user
        ).select_related('order', 'addon')


class OrderPhotoApiView(AbstractBaseListApiView):
    serializer_class = OrderPhotoSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['order', 'is_primary']
    ordering_fields = ['is_primary', 'created_at']
    ordering = ['-is_primary', '-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return OrderPhoto.objects.filter(
            order__is_deleted=False,
            order__client__user_profile__user=user
        ).select_related('order')


class BidApiView(AbstractBaseListApiView):
    serializer_class = BidSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['status', 'order', 'is_negotiable']
    ordering_fields = ['amount', 'created_at']
    ordering = ['amount', '-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return Bid.objects.filter(
            order__is_deleted=False,
            order__client__user_profile__user=user
        ).select_related('order', 'provider__user_profile__user')


class BidCreateApiView(generics.CreateAPIView):
    serializer_class = BidCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id, is_deleted=False)
        # Get the service provider profile for the current user
        provider_profile = get_object_or_404(
            'users.ServiceProviderProfile', 
            user_profile__user=self.request.user
        )
        serializer.save(order=order, provider=provider_profile)


class OrderDisputeApiView(AbstractBaseListApiView):
    serializer_class = OrderDisputeSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['dispute_type', 'status', 'order']
    search_fields = ['description', 'admin_notes']
    ordering_fields = ['dispute_type', 'status', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return OrderDispute.objects.filter(
            order__is_deleted=False,
            order__client__user_profile__user=user
        ).select_related('order')


class OrderDisputeCreateApiView(generics.CreateAPIView):
    serializer_class = OrderDisputeCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id, is_deleted=False)
        serializer.save(order=order)


class OrderDisputeDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderDisputeUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return OrderDispute.objects.filter(
            order__is_deleted=False,
            order__client__user_profile__user=user
        ).select_related('order')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderDisputeSerializer
        return OrderDisputeUpdateSerializer
