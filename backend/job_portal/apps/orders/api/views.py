# Django imports
from django.db import models, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from job_portal.apps.chat.models import ChatParticipant, ChatRoom

# DRF imports
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from utils.exceptions import StandardizedViewMixin
from utils.pagination import CustomPagination
from utils.permissions import (
    HasClientProfile,
    HasServiceProviderProfile,
    HasSpecificPermission,
)

from ..models import Bid, Order, OrderAssignment
from .serializers import (
    BidActionSerializer,
    BidCreateUpdateSerializer,
    BidSerializer,
    OrderAssignmentSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
)


class OrderApiView(StandardizedViewMixin, generics.ListAPIView):
    """List all orders (admin view)."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, HasSpecificPermission(["orders.view_order"])]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "service_subcategory", "urgency"]
    search_fields = ["title", "description", "location", "city", "state"]
    ordering_fields = ["created_at", "service_date", "budget_min", "budget_max"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Order.objects.all().select_related(
            "client__user_profile", "service_subcategory"
        )


class MyOrdersView(StandardizedViewMixin, generics.ListAPIView):
    """Get current user's orders (as client)."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, HasClientProfile]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "service_subcategory", "urgency"]
    search_fields = ["title", "description", "location", "city", "state"]
    ordering_fields = ["created_at", "service_date", "budget_min", "budget_max"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(client__user_profile__user=user).select_related(
            "client__user_profile", "service_subcategory"
        )


class OrderDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = OrderUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            client__user_profile__user=user,
        ).select_related("client__user_profile", "service_subcategory")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderSerializer
        return OrderUpdateSerializer


class OrderCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [
        IsAuthenticated,
        HasClientProfile,
        HasSpecificPermission(["orders.add_order"]),
    ]

    def perform_create(self, serializer):
        client_profile = self.request.user.job_portal_profile.client_profile
        serializer.save(client=client_profile)




class BidApiView(StandardizedViewMixin, generics.ListAPIView):
    """List all bids (admin view)."""
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, HasSpecificPermission(["orders.view_bid"])]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "order", "is_negotiable"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["amount", "-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Bid.objects.all().select_related("order", "provider__user_profile")


class MyBidsView(StandardizedViewMixin, generics.ListAPIView):
    """Get current user's bids (as service provider)."""
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "order", "is_negotiable"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["amount", "-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Bid.objects.filter(
            provider__user_profile__user=user
        ).select_related("order", "provider__user_profile")


class OrderBidsView(StandardizedViewMixin, generics.ListAPIView):
    """Get bids for current user's orders (as client)."""
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, HasClientProfile]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "is_negotiable"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["amount", "-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Bid.objects.filter(
            order__client__user_profile__user=user
        ).select_related("order", "provider__user_profile")


class BidCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = BidCreateUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        HasServiceProviderProfile,
        HasSpecificPermission(["orders.add_bid"]),
    ]

    def perform_create(self, serializer):
        order_id = self.kwargs.get("order_id")
        order = get_object_or_404(
            Order, id=order_id, status__in=["published", "bidding"]
        )
        provider_profile = self.request.user.job_portal_profile.service_provider_profile

        # Check if provider already has a bid on this order
        existing_bid = Bid.objects.filter(
            order=order, provider=provider_profile
        ).first()

        if existing_bid:

            raise ValidationError("You have already submitted a bid for this order")

        serializer.save(order=order, provider=provider_profile)




class BidDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidCreateUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        HasSpecificPermission(["orders.view_bid", "orders.change_bid"]),
    ]

    def get_queryset(self):
        user = self.request.user
        # Allow both clients (order owners) and providers (bid owners) to access
        return Bid.objects.filter(
            models.Q(order__client__user_profile__user=user)
            | models.Q(provider__user_profile__user=user)
        ).select_related("order", "provider__user_profile")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BidSerializer
        return BidCreateUpdateSerializer


class BidAcceptApiView(StandardizedViewMixin, APIView):
    """Accept a bid and create order assignment."""
    serializer_class = BidActionSerializer
    permission_classes = [IsAuthenticated, HasClientProfile]

    @transaction.atomic
    def post(self, request, bid_id):
        try:
            bid = get_object_or_404(
                Bid.objects.select_related("order", "provider"),
                id=bid_id,
                order__client__user_profile__user=request.user,
                status="pending",
            )

            # Check if order already has an assignment
            if hasattr(bid.order, "assignment"):
                return Response(
                    {"error": "Order already has an accepted bid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update bid status
            bid.status = "accepted"
            bid.accepted_at = timezone.now()
            bid.save()

            # Reject all other bids for this order
            Bid.objects.filter(order=bid.order, status="pending").exclude(
                id=bid.id
            ).update(status="rejected", rejected_at=timezone.now())

            # Update order status
            bid.order.status = "assigned"
            bid.order.assigned_at = timezone.now()
            bid.order.final_price = bid.amount
            bid.order.save()

            # Create order assignment (get_or_create to avoid duplicates)
            assignment, created = OrderAssignment.objects.get_or_create(
                order=bid.order,
                defaults={"provider": bid.provider, "accepted_bid": bid},
            )

            # Add provider to chat room when bid is accepted
            self._add_provider_to_chat(bid.order, bid.provider)

            return Response(
                {
                    "message": "Bid accepted successfully",
                    "bid": BidSerializer(bid).data,
                    "assignment": OrderAssignmentSerializer(assignment).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to accept bid: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def _add_provider_to_chat(self, order, provider):
        """Add provider to order's chat room."""
        try:
            # Get or create chat room for this order
            chat_room = ChatRoom.objects.filter(order=order).first()
            if not chat_room:
                chat_room = order._create_chat_room()
            
            # Add provider as participant if not already added
            ChatParticipant.objects.get_or_create(
                chat_room=chat_room,
                user=provider.user_profile.user,
                defaults={'role': 'member'}
            )
        except Exception as e:
            # Log error but don't fail the bid acceptance
            print(f"Failed to add provider to chat: {e}")


class BidRejectApiView(StandardizedViewMixin, APIView):
    """Reject a bid."""

    permission_classes = [IsAuthenticated, HasClientProfile]
    serializer_class = BidActionSerializer

    def post(self, request, bid_id):
        serializer = BidActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            bid = get_object_or_404(
                Bid,
                id=bid_id,
                order__client__user_profile__user=request.user,
                status="pending",
            )

            bid.status = "rejected"
            bid.rejected_at = timezone.now()
            bid.save()

            return Response(
                {
                    "message": "Bid rejected successfully",
                    "bid": BidSerializer(bid).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to reject bid: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class BidWithdrawApiView(StandardizedViewMixin, APIView):
    """Withdraw a bid (by provider)."""

    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    serializer_class = BidActionSerializer

    def post(self, request, bid_id):
        serializer = BidActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            bid = get_object_or_404(
                Bid,
                id=bid_id,
                provider__user_profile__user=request.user,
                status="pending",
            )

            bid.status = "withdrawn"
            bid.withdrawn_at = timezone.now()
            bid.save()

            return Response(
                {
                    "message": "Bid withdrawn successfully",
                    "bid": BidSerializer(bid).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to withdraw bid: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class OrderAssignmentApiView(StandardizedViewMixin, generics.ListAPIView):
    """List all order assignments (admin view)."""

    serializer_class = OrderAssignmentSerializer
    permission_classes = [IsAuthenticated, HasSpecificPermission(["orders.view_orderassignment"])]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["order", "provider"]
    ordering_fields = ["assigned_at", "start_date"]
    ordering = ["-assigned_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        return OrderAssignment.objects.all().select_related("order", "provider__user_profile", "accepted_bid")


class MyAssignmentsView(StandardizedViewMixin, generics.ListAPIView):
    """Get current user's assignments (as service provider)."""

    serializer_class = OrderAssignmentSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["order"]
    ordering_fields = ["assigned_at", "start_date"]
    ordering = ["-assigned_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return OrderAssignment.objects.filter(
            provider__user_profile__user=user
        ).select_related("order", "provider__user_profile", "accepted_bid")


class MyOrderAssignmentsView(StandardizedViewMixin, generics.ListAPIView):
    """Get assignments for current user's orders (as client)."""

    serializer_class = OrderAssignmentSerializer
    permission_classes = [IsAuthenticated, HasClientProfile]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["provider"]
    ordering_fields = ["assigned_at", "start_date"]
    ordering = ["-assigned_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return OrderAssignment.objects.filter(
            order__client__user_profile__user=user
        ).select_related("order", "provider__user_profile", "accepted_bid")


class OrderAssignmentDetailApiView(
    StandardizedViewMixin, generics.RetrieveUpdateAPIView
):
    """View and update order assignment details."""

    serializer_class = OrderAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return OrderAssignment.objects.filter(
            models.Q(order__client__user_profile__user=user)
            | models.Q(provider__user_profile__user=user)
        ).select_related("order", "provider__user_profile", "accepted_bid")
