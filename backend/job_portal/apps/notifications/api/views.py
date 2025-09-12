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
from ..models import UserNotification, NotificationTemplate, NotificationPreference
from .serializers import (
    NotificationSerializer, NotificationTemplateSerializer, NotificationSettingSerializer,
    NotificationCreateSerializer, NotificationUpdateSerializer,
    NotificationSettingUpdateSerializer, NotificationTemplateCreateSerializer,
    NotificationTemplateUpdateSerializer, NotificationSettingCreateSerializer
)


class NotificationApiView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['priority', 'is_read']
    search_fields = ['subject', 'message']
    ordering_fields = ['priority', 'created_at', 'read_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        return UserNotification.objects.filter(
            user=user,
        ).select_related('user')
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications for current user."""
        notifications = UserNotification.objects.filter(
            user=request.user, is_read=False,
        ).select_related('user')
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notifications (last 7 days)."""
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        
        notifications = UserNotification.objects.filter(
            user=request.user, created_at__gte=week_ago,
        ).select_related('user')
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read for current user."""
        UserNotification.objects.filter(
            user=request.user, is_read=False,
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get notification counts for current user."""
        total = UserNotification.objects.filter(
            user=request.user,
        ).count()
        
        unread = UserNotification.objects.filter(
            user=request.user, is_read=False,
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
            user=self.request.user,
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


class NotificationSettingApiView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSettingUpdateSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get_object(self):
        # Get or create notification preferences for the current user
        obj, created = NotificationPreference.objects.get_or_create(
            user=self.request.user,
            defaults={
                'email_notifications': True,
                'push_notifications': True,
                'sms_notifications': False,
                'in_app_notifications': True,
                'order_updates': True,
                'bid_notifications': True,
                'payment_notifications': True,
                'chat_notifications': True,
                'promotional_notifications': False,
                'system_notifications': True,
                'timezone': 'UTC',
                'digest_frequency': 'immediate',
            }
        )
        return obj
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NotificationSettingSerializer
        return NotificationSettingUpdateSerializer




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
        return NotificationTemplate.objects.all()


class NotificationTemplateDetailApiView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationTemplateUpdateSerializer
    permission_classes = [HasSpecificPermission(['notifications.change_notificationtemplate'])]
    
    def get_queryset(self):
        return NotificationTemplate.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NotificationTemplateSerializer
        return NotificationTemplateUpdateSerializer


class NotificationTemplateCreateApiView(generics.CreateAPIView):
    serializer_class = NotificationTemplateCreateSerializer
    permission_classes = [HasSpecificPermission(['notifications.add_notificationtemplate'])]
