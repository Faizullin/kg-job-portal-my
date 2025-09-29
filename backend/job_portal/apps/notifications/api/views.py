from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.pagination import CustomPagination
from utils.permissions import HasSpecificPermission

from ..models import Notification
from .serializers import (
    NotificationCreateSerializer,
    NotificationSerializer,
    NotificationUpdateSerializer,
)


class NotificationApiView(generics.ListAPIView):
    """List notifications for the current user."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_read"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "read_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(
            recipient=user,
        ).select_related("recipient", "actor", "target")


class NotificationDetailApiView(generics.RetrieveUpdateAPIView):
    """Retrieve and update individual notifications."""

    serializer_class = NotificationUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
        ).select_related("recipient", "actor", "target")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return NotificationSerializer
        return NotificationUpdateSerializer

    def perform_update(self, serializer):
        if serializer.validated_data.get("is_read") and not serializer.instance.is_read:
            serializer.save(read_at=timezone.now())
        else:
            serializer.save()


class NotificationCreateApiView(generics.CreateAPIView):
    """Create new notifications (admin only)."""

    serializer_class = NotificationCreateSerializer
    permission_classes = [HasSpecificPermission(["notifications.add_notification"])]


class NotificationUnreadView(generics.ListAPIView):
    """Get unread notifications for current user."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
            is_read=False,
        ).select_related("recipient", "actor", "target")


class NotificationRecentView(generics.ListAPIView):
    """Get recent notifications (last 7 days)."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        week_ago = timezone.now() - timedelta(days=7)

        return Notification.objects.filter(
            recipient=self.request.user,
            created_at__gte=week_ago,
        ).select_related("recipient", "actor", "target")


class NotificationMarkAllReadView(APIView):
    """Mark all notifications as read for current user."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())

        return Response({"message": "All notifications marked as read"})


class NotificationCountView(APIView):
    """Get notification counts for current user."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = Notification.objects.filter(
            recipient=request.user,
        ).count()

        unread = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()

        return Response({"total": total, "unread": unread})
