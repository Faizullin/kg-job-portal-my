from utils.exceptions import StandardizedViewMixin
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction, models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from utils.permissions import (
    HasSpecificPermission,
    HasClientProfile,
    HasServiceProviderProfile,
)
from utils.pagination import CustomPagination
from ..models import Order, OrderAddon, OrderPhoto, Bid, OrderDispute, OrderAssignment
from .serializers import (
    OrderSerializer,
    OrderAddonSerializer,
    OrderPhotoSerializer,
    BidSerializer,
    OrderDisputeSerializer,
    OrderCreateSerializer,
    OrderUpdateSerializer,
    BidCreateUpdateSerializer,
    OrderDisputeCreateSerializer,
    OrderDisputeUpdateSerializer,
    BidActionSerializer,
    OrderAssignmentSerializer,
)


class OrderApiView(StandardizedViewMixin, generics.ListAPIView):
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
            "client__user_profile__user", "service_subcategory"
        )

    @action(detail=False, methods=["get"])
    def my_orders(self, request):
        """Get orders where user is the client."""
        orders = Order.objects.filter(
            client__user_profile__user=request.user,
        ).select_related("service_subcategory")

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = OrderUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        HasSpecificPermission(["orders.view_order", "orders.change_order"]),
    ]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            client__user_profile__user=user,
        ).select_related("client__user_profile__user", "service_subcategory")

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
        # Django automatically caches the profile when accessed
        client_profile = self.request.user.job_portal_profile.client_profile
        serializer.save(client=client_profile)


class OrderAddonApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = OrderAddonSerializer
    permission_classes = [
        IsAuthenticated,
        HasSpecificPermission(["orders.view_orderaddon"]),
    ]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["order"]
    search_fields = ["addon__name"]
    ordering_fields = ["quantity", "price", "created_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return OrderAddon.objects.filter(
            order__client__user_profile__user=user
        ).select_related("order", "addon")


class OrderPhotoApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = OrderPhotoSerializer
    permission_classes = [
        IsAuthenticated,
        HasSpecificPermission(["orders.view_orderphoto"]),
    ]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["order", "is_primary"]
    ordering_fields = ["is_primary", "created_at"]
    ordering = ["-is_primary", "-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return OrderPhoto.objects.filter(
            order__client__user_profile__user=user
        ).select_related("order")


class BidApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "order", "is_negotiable"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["amount", "-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        # Return bids based on user role:
        # - Clients see bids on their orders
        # - Providers see their own bids
        try:
            if hasattr(user, "job_portal_profile"):
                if user.job_portal_profile.user_type in ["client", "both"]:
                    return Bid.objects.filter(
                        order__client__user_profile__user=user
                    ).select_related("order", "provider__user_profile__user")
                elif user.job_portal_profile.user_type in ["service_provider", "both"]:
                    return Bid.objects.filter(
                        provider__user_profile__user=user
                    ).select_related("order", "provider__user_profile__user")
        except:
            pass

        # Fallback: return empty queryset
        return Bid.objects.none()


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
            from rest_framework.exceptions import ValidationError

            raise ValidationError("You have already submitted a bid for this order")

        serializer.save(order=order, provider=provider_profile)


class OrderDisputeApiView(StandardizedViewMixin, generics.ListAPIView):
    serializer_class = OrderDisputeSerializer
    permission_classes = [
        IsAuthenticated,
        HasSpecificPermission(["orders.view_orderdispute"]),
    ]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["dispute_type", "status", "order"]
    search_fields = ["description", "admin_notes"]
    ordering_fields = ["dispute_type", "status", "created_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return OrderDispute.objects.filter(
            order__client__user_profile__user=user
        ).select_related("order")


class OrderDisputeCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = OrderDisputeCreateSerializer
    permission_classes = [
        IsAuthenticated,
        HasClientProfile,
        HasSpecificPermission(["orders.add_orderdispute"]),
    ]

    def perform_create(self, serializer):
        order_id = self.kwargs.get("order_id")
        order = get_object_or_404(
            Order, id=order_id, client__user_profile__user=self.request.user
        )
        serializer.save(order=order, raised_by=self.request.user)


class OrderDisputeDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = OrderDisputeUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        HasSpecificPermission(
            ["orders.view_orderdispute", "orders.change_orderdispute"]
        ),
    ]

    def get_queryset(self):
        user = self.request.user
        return OrderDispute.objects.filter(
            order__client__user_profile__user=user
        ).select_related("order")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderDisputeSerializer
        return OrderDisputeUpdateSerializer


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
        ).select_related("order", "provider__user_profile__user")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BidSerializer
        return BidCreateUpdateSerializer


class BidAcceptApiView(StandardizedViewMixin, APIView):
    """Accept a bid and create order assignment."""

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
    """List order assignments."""

    serializer_class = OrderAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["order", "provider"]
    ordering_fields = ["assigned_at", "start_date"]
    ordering = ["-assigned_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        # Show assignments where user is either client or provider
        return OrderAssignment.objects.filter(
            models.Q(order__client__user_profile__user=user)
            | models.Q(provider__user_profile__user=user)
        ).select_related("order", "provider__user_profile__user", "accepted_bid")


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
        ).select_related("order", "provider__user_profile__user", "accepted_bid")
