from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from utils.pagination import CustomPagination
from utils.permissions import HasSpecificPermission

from ..models import Notification
from .serializers import (
    NotificationCreateSerializer,
    NotificationSerializer,
    NotificationUpdateSerializer,
)


class NotificationAPIViewSet(ModelViewSet):
    """
    ViewSet for managing notifications with clean actions.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_read", "level"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "read_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        """Return notifications for the current user."""
        return Notification.objects.filter(
            recipient=self.request.user,
        ).select_related("recipient", "actor", "target")

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return NotificationCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return NotificationUpdateSerializer
        return NotificationSerializer

    def perform_update(self, serializer):
        """Handle read status update with timestamp."""
        if serializer.validated_data.get("is_read") and not serializer.instance.is_read:
            serializer.save(read_at=timezone.now())
        else:
            serializer.save()

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == "create":
            permission_classes = [HasSpecificPermission(["notifications.add_notification"])()]
        else:
            permission_classes = [IsAuthenticated]
        return permission_classes

    @extend_schema(
        description="Get unread notifications for current user",
        responses={200: NotificationSerializer(many=True)},
        operation_id="v1_notifications_unread"
    )
    @action(detail=False, methods=['get'], url_path='unread')
    def unread(self, request):
        """Get unread notifications for current user."""
        queryset = self.get_queryset().filter(is_read=False)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Get recent notifications (last 7 days)",
        parameters=[
            OpenApiParameter(name='days', description='Number of days to look back', type=int, default=7),
        ],
        responses={200: NotificationSerializer(many=True)},
        operation_id="v1_notifications_recent"
    )
    @action(detail=False, methods=['get'], url_path='recent')
    def recent(self, request):
        """Get recent notifications."""
        days = int(request.query_params.get('days', 7))
        cutoff_date = timezone.now() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(created_at__gte=cutoff_date)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Mark all notifications as read for current user",
        responses={200: {"message": "All notifications marked as read"}},
        operation_id="v1_notifications_mark_all_read"
    )
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """Mark all notifications as read for current user."""
        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())

        return Response({
            "message": f"Marked {updated_count} notifications as read"
        })

    @extend_schema(
        description="Get notification counts for current user",
        responses={200: {"total": 10, "unread": 3}},
        operation_id="v1_notifications_count"
    )
    @action(detail=False, methods=['get'], url_path='count')
    def count(self, request):
        """Get notification counts for current user."""
        queryset = self.get_queryset()
        
        total = queryset.count()
        unread = queryset.filter(is_read=False).count()
        
        return Response({
            "total": total,
            "unread": unread
        })

    @extend_schema(
        description="Mark specific notification as read",
        responses={200: NotificationSerializer},
        operation_id="v1_notifications_mark_read"
    )
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Mark specific notification as read."""
        notification = self.get_object()
        
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @extend_schema(
        description="Mark specific notification as unread",
        responses={200: NotificationSerializer},
        operation_id="v1_notifications_mark_unread"
    )
    @action(detail=True, methods=['post'], url_path='mark-unread')
    def mark_unread(self, request, pk=None):
        """Mark specific notification as unread."""
        notification = self.get_object()
        
        if notification.is_read:
            notification.is_read = False
            notification.read_at = None
            notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
