from datetime import timedelta

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.permissions import IsAuthenticated
from utils.exceptions import StandardizedViewMixin
from utils.permissions import HasSpecificPermission
from utils.pagination import CustomPagination
from ..models import UserNotification
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer, NotificationUpdateSerializer
)


class NotificationApiView(StandardizedViewMixin, generics.ListAPIView):
    """List notifications for the current user."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    search_fields = ['title', 'message']
    ordering_fields = ['notification_type', 'created_at', 'read_at']
    ordering = ['-created_at']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        return UserNotification.objects.filter(
            user=user,
        ).select_related('user', 'order', 'bid')


class NotificationDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    """Retrieve and update individual notifications."""
    serializer_class = NotificationUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserNotification.objects.filter(
            user=self.request.user,
        ).select_related('user', 'order', 'bid')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NotificationSerializer
        return NotificationUpdateSerializer
    
    def perform_update(self, serializer):
        if serializer.validated_data.get('is_read') and not serializer.instance.is_read:
            serializer.save(read_at=timezone.now())
        else:
            serializer.save()


class NotificationCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    """Create new notifications (admin only)."""
    serializer_class = NotificationCreateSerializer
    permission_classes = [HasSpecificPermission(['notifications.add_notification'])]


class NotificationUnreadView(StandardizedViewMixin, generics.ListAPIView):
    """Get unread notifications for current user."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return UserNotification.objects.filter(
            user=self.request.user, is_read=False,
        ).select_related('user', 'order', 'bid')


class NotificationRecentView(StandardizedViewMixin, generics.ListAPIView):
    """Get recent notifications (last 7 days)."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        week_ago = timezone.now() - timedelta(days=7)
        
        return UserNotification.objects.filter(
            user=self.request.user, created_at__gte=week_ago,
        ).select_related('user', 'order', 'bid')


class NotificationMarkAllReadView(StandardizedViewMixin, APIView):
    """Mark all notifications as read for current user."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        UserNotification.objects.filter(
            user=request.user, is_read=False,
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({'message': 'All notifications marked as read'})


class NotificationCountView(StandardizedViewMixin, APIView):
    """Get notification counts for current user."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
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