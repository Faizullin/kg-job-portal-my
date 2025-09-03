from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from utils.permissions import AbstractIsAuthenticatedOrReadOnly, HasSpecificPermission
from utils.pagination import CustomPagination
from ..models import UserNotification, NotificationTemplate, NotificationPreference, NotificationLog
from .serializers import (
    NotificationSerializer, NotificationTemplateSerializer, NotificationSettingSerializer,
    NotificationLogSerializer, NotificationCreateSerializer, NotificationUpdateSerializer,
    NotificationSettingUpdateSerializer, NotificationTemplateCreateSerializer,
    NotificationTemplateUpdateSerializer, NotificationSettingCreateSerializer
)


class NotificationApiView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'priority', 'is_read']
    search_fields = ['title', 'message']
    ordering_fields = ['priority', 'created_at', 'read_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        return UserNotification.objects.filter(
            user=user, is_deleted=False
        ).select_related('user')
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications for current user."""
        notifications = UserNotification.objects.filter(
            user=request.user, is_read=False, is_deleted=False
        ).select_related('user')
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notifications (last 7 days)."""
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        
        notifications = UserNotification.objects.filter(
            user=request.user, created_at__gte=week_ago, is_deleted=False
        ).select_related('user')
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read for current user."""
        UserNotification.objects.filter(
            user=request.user, is_read=False, is_deleted=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get notification counts for current user."""
        total = UserNotification.objects.filter(
            user=request.user, is_deleted=False
        ).count()
        
        unread = UserNotification.objects.filter(
            user=request.user, is_read=False, is_deleted=False
        ).count()
        
        return Response({
            'total': total,
            'unread': unread
        })


class NotificationDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return UserNotification.objects.filter(
            user=self.request.user, is_deleted=False
        ).select_related('user')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NotificationSerializer
        return NotificationUpdateSerializer
    
    def perform_update(self, serializer):
        if serializer.validated_data.get('is_read') and not serializer.instance.is_read:
            serializer.save(read_at=timezone.now())
        else:
            serializer.save()


class NotificationCreateApiView(generics.CreateAPIView):
    serializer_class = NotificationCreateSerializer
    permission_classes = [HasSpecificPermission(['notifications.add_notification'])]


class NotificationSettingApiView(generics.ListAPIView):
    serializer_class = NotificationSettingSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['email_notifications', 'push_notifications']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return NotificationPreference.objects.filter(
            user=self.request.user, is_deleted=False
        ).select_related('user')


class NotificationSettingDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSettingUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return NotificationPreference.objects.filter(
            user=self.request.user, is_deleted=False
        ).select_related('user')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NotificationSettingSerializer
        return NotificationSettingUpdateSerializer


class NotificationSettingCreateApiView(generics.CreateAPIView):
    serializer_class = NotificationSettingCreateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationTemplateApiView(generics.ListAPIView):
    serializer_class = NotificationTemplateSerializer
    permission_classes = [HasSpecificPermission(['notifications.add_notificationtemplate'])]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'is_active']
    search_fields = ['name', 'subject', 'content']
    ordering_fields = ['name', 'notification_type', 'created_at']
    ordering = ['name']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return NotificationTemplate.objects.filter(is_deleted=False)


class NotificationTemplateDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationTemplateUpdateSerializer
    permission_classes = [HasSpecificPermission(['notifications.change_notificationtemplate'])]
    
    def get_queryset(self):
        return NotificationTemplate.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NotificationTemplateSerializer
        return NotificationTemplateUpdateSerializer


class NotificationTemplateCreateApiView(generics.CreateAPIView):
    serializer_class = NotificationTemplateCreateSerializer
    permission_classes = [HasSpecificPermission(['notifications.add_notificationtemplate'])]


class NotificationLogApiView(generics.ListAPIView):
    serializer_class = NotificationLogSerializer
    permission_classes = [HasSpecificPermission(['notifications.add_notification'])]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'delivery_method', 'user']
    ordering_fields = ['sent_at', 'delivered_at', 'created_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return NotificationLog.objects.filter(is_deleted=False).select_related('notification', 'user')
    
    @action(detail=False, methods=['get'])
    def failed(self, request):
        """Get failed notification deliveries."""
        failed_logs = NotificationLog.objects.filter(
            status='failed', is_deleted=False
        ).select_related('notification', 'user')
        
        serializer = NotificationLogSerializer(failed_logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending notification deliveries."""
        pending_logs = NotificationLog.objects.filter(
            status='pending', is_deleted=False
        ).select_related('notification', 'user')
        
        serializer = NotificationLogSerializer(pending_logs, many=True)
        return Response(serializer.data)
