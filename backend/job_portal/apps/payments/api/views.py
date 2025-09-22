from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.permissions import IsAuthenticated
from utils.permissions import HasSpecificPermission
from utils.exceptions import StandardizedViewMixin
from utils.decorators import GroupRequiredMixin, RateLimitMixin, LogActionMixin
from utils.pagination import CustomPagination
from ..models import Payment, PaymentMethod, Invoice, StripeWebhookEvent
from .serializers import (
    PaymentSerializer, PaymentMethodSerializer,
    InvoiceSerializer, PaymentCreateSerializer,
    PaymentMethodCreateSerializer, PaymentMethodUpdateSerializer,
    InvoiceCreateSerializer
)


class PaymentApiView(StandardizedViewMixin, GroupRequiredMixin, RateLimitMixin, LogActionMixin, generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'currency']
    search_fields = ['invoice__order__title', 'payment_id']
    ordering_fields = ['amount', 'created_at', 'updated_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    # Rate limiting configuration
    max_requests = 500
    window = 3600  # 1 hour
    
    # Permission groups
    group_required = 'Payment Managers'  # Can be overridden per user
    
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(
            payment_method__user=user, 
        ).select_related('invoice__order', 'payment_method')
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending payments."""
        payments = Payment.objects.filter(
            payment_method__user=request.user, status='pending',
        ).select_related('invoice__order', 'payment_method')
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed payments."""
        payments = Payment.objects.filter(
            payment_method__user=request.user, status='completed', 
        ).select_related('invoice__order', 'payment_method')
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentDetailApiView(StandardizedViewMixin, GroupRequiredMixin, RateLimitMixin, LogActionMixin, generics.RetrieveUpdateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]
    
    # Rate limiting configuration
    max_requests = 500
    window = 3600  # 1 hour
    
    # Permission groups
    group_required = 'Payment Managers'
    
    def get_queryset(self):
        return Payment.objects.filter(
            payment_method__user=self.request.user, 
        ).select_related('invoice__order', 'payment_method')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PaymentSerializer
        return PaymentCreateSerializer


class PaymentCreateApiView(StandardizedViewMixin, GroupRequiredMixin, RateLimitMixin, LogActionMixin, generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]
    
    # Rate limiting configuration
    max_requests = 500
    window = 3600  # 1 hour
    
    # Permission groups
    group_required = 'Payment Managers'


class PaymentMethodApiView(StandardizedViewMixin, GroupRequiredMixin, RateLimitMixin, LogActionMixin, generics.ListAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['method_type', 'is_active', 'is_default']
    ordering_fields = ['is_default', 'created_at']
    ordering = ['-is_default', '-created_at']
    pagination_class = CustomPagination
    
    # Rate limiting configuration
    max_requests = 500
    window = 3600  # 1 hour
    
    # Permission groups
    group_required = 'Payment Managers'
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(
            user=self.request.user, 
        )


class PaymentMethodDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentMethodUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(
            user=self.request.user, 
        )
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PaymentMethodSerializer
        return PaymentMethodUpdateSerializer


class PaymentMethodCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = PaymentMethodCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InvoiceApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'order']
    ordering_fields = ['total_amount', 'due_date', 'created_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.filter(
            order__client__user_profile__user=user, 
        ).select_related('order')


class InvoiceDetailApiView(StandardizedViewMixin, generics.RetrieveAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.filter(
            order__client__user_profile__user=user, 
        ).select_related('order')


class InvoiceCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = InvoiceCreateSerializer
    permission_classes = [HasSpecificPermission(['payments.add_invoice'])]
