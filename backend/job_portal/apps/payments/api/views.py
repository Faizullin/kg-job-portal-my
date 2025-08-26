from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404

from utils.crud_base.views import AbstractBaseListApiView, AbstractBaseApiView
from utils.permissions import AbstractIsAuthenticatedOrReadOnly, AbstractHasSpecificPermission
from utils.decorators import GroupRequiredMixin, RateLimitMixin, LogActionMixin
from ..models import Payment, PaymentMethod, Invoice, PaymentProvider, StripeWebhookEvent
from .serializers import (
    PaymentSerializer, PaymentMethodSerializer,
    InvoiceSerializer, PaymentCreateSerializer,
    PaymentMethodCreateSerializer, PaymentMethodUpdateSerializer,
    InvoiceCreateSerializer
)


class PaymentApiView(GroupRequiredMixin, RateLimitMixin, LogActionMixin, AbstractBaseListApiView):
    serializer_class = PaymentSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['status', 'payment_type', 'currency']
    search_fields = ['order__title', 'transaction_id']
    ordering_fields = ['amount', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    # Rate limiting configuration
    max_requests = 500
    window = 3600  # 1 hour
    
    # Permission groups
    group_required = 'Payment Managers'  # Can be overridden per user
    
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(
            user=user, is_deleted=False
        ).select_related('order', 'payment_method').prefetch_related('transactions')
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending payments."""
        payments = Payment.objects.filter(
            user=request.user, status='pending', is_deleted=False
        ).select_related('order', 'payment_method')
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed payments."""
        payments = Payment.objects.filter(
            user=request.user, status='completed', is_deleted=False
        ).select_related('order', 'payment_method')
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentDetailApiView(GroupRequiredMixin, RateLimitMixin, LogActionMixin, generics.RetrieveUpdateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    # Rate limiting configuration
    max_requests = 500
    window = 3600  # 1 hour
    
    # Permission groups
    group_required = 'Payment Managers'
    
    def get_queryset(self):
        return Payment.objects.filter(
            user=self.request.user, is_deleted=False
        ).select_related('order', 'payment_method')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PaymentSerializer
        return PaymentCreateSerializer


class PaymentCreateApiView(GroupRequiredMixin, RateLimitMixin, LogActionMixin, generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    # Rate limiting configuration
    max_requests = 500
    window = 3600  # 1 hour
    
    # Permission groups
    group_required = 'Payment Managers'
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentMethodApiView(GroupRequiredMixin, RateLimitMixin, LogActionMixin, AbstractBaseListApiView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['method_type', 'is_active', 'is_default']
    ordering_fields = ['is_default', 'created_at']
    ordering = ['-is_default', '-created_at']
    
    # Rate limiting configuration
    max_requests = 500
    window = 3600  # 1 hour
    
    # Permission groups
    group_required = 'Payment Managers'
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(
            user=self.request.user, is_deleted=False
        )


class PaymentMethodDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentMethodUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(
            user=self.request.user, is_deleted=False
        )
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PaymentMethodSerializer
        return PaymentMethodUpdateSerializer


class PaymentMethodCreateApiView(generics.CreateAPIView):
    serializer_class = PaymentMethodCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InvoiceApiView(AbstractBaseListApiView):
    serializer_class = InvoiceSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filterset_fields = ['status', 'order']
    ordering_fields = ['total_amount', 'due_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.filter(
            order__client__user_profile__user=user, is_deleted=False
        ).select_related('order')


class InvoiceDetailApiView(generics.RetrieveAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.filter(
            order__client__user_profile__user=user, is_deleted=False
        ).select_related('order')


class InvoiceCreateApiView(generics.CreateAPIView):
    serializer_class = InvoiceCreateSerializer
    permission_classes = [AbstractHasSpecificPermission(['payments.add_invoice'])]
