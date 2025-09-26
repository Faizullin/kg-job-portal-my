# Django imports
from django.db import transaction
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
from rest_framework.parsers import MultiPartParser, FormParser

# Local imports
from utils.exceptions import StandardizedViewMixin
from utils.pagination import CustomPagination
from utils.permissions import (
    HasClientProfile,
    HasServiceProviderProfile,
    HasSpecificPermission,
)

from ..models import Bid, Order, OrderAssignment, OrderAttachment
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "order", "provider"]
    search_fields = ["description", "order__title"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Bid.objects.all().select_related(
            "order__client__user_profile", "provider__user_profile"
        )


class BidCreateApiView(StandardizedViewMixin, generics.CreateAPIView):
    serializer_class = BidCreateUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        HasServiceProviderProfile,
        HasSpecificPermission(["orders.add_bid"]),
    ]

    def perform_create(self, serializer):
        order_id = self.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        provider_profile = self.request.user.job_portal_profile.service_provider_profile
        serializer.save(order=order, provider=provider_profile)


class BidDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Bid.objects.filter(
            provider__user_profile__user=user,
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
                    "assignment_id": assignment.id,
                    "order_status": bid.order.status,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to accept bid: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    def _add_provider_to_chat(self, order, provider):
        """Add provider to order's chat room."""
        try:
            chat_room = ChatRoom.objects.get(order=order)
            ChatParticipant.objects.get_or_create(
                chat_room=chat_room,
                user=provider.user_profile.user,
                defaults={"role": "member"},
            )
        except ChatRoom.DoesNotExist:
            pass


class BidRejectApiView(StandardizedViewMixin, APIView):
    """Reject a bid."""
    serializer_class = BidActionSerializer
    permission_classes = [IsAuthenticated, HasClientProfile]

    def post(self, request, bid_id):
        try:
            bid = get_object_or_404(
                Bid.objects.select_related("order"),
                id=bid_id,
                order__client__user_profile__user=request.user,
                status="pending",
            )

            bid.status = "rejected"
            bid.rejected_at = timezone.now()
            bid.save()

            return Response(
                {"message": "Bid rejected successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to reject bid: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BidWithdrawApiView(StandardizedViewMixin, APIView):
    """Withdraw a bid."""
    serializer_class = BidActionSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]

    def post(self, request, bid_id):
        try:
            bid = get_object_or_404(
                Bid.objects.select_related("order"),
                id=bid_id,
                provider__user_profile__user=request.user,
                status="pending",
            )

            bid.status = "withdrawn"
            bid.withdrawn_at = timezone.now()
            bid.save()

            return Response(
                {"message": "Bid withdrawn successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to withdraw bid: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyBidsView(StandardizedViewMixin, generics.ListAPIView):
    """Get current user's bids (as provider)."""
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "order"]
    search_fields = ["description", "order__title"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Bid.objects.filter(
            provider__user_profile__user=user
        ).select_related("order__client__user_profile", "provider__user_profile")


class OrderBidsView(StandardizedViewMixin, generics.ListAPIView):
    """Get bids for current user's orders (as client)."""
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, HasClientProfile]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "order"]
    search_fields = ["description", "provider__user_profile__user__first_name"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["-created_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Bid.objects.filter(
            order__client__user_profile__user=user
        ).select_related("order__client__user_profile", "provider__user_profile")


class OrderAssignmentApiView(StandardizedViewMixin, generics.ListAPIView):
    """List all order assignments (admin view)."""
    serializer_class = OrderAssignmentSerializer
    permission_classes = [IsAuthenticated, HasSpecificPermission(["orders.view_orderassignment"])]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["provider", "order__status"]
    search_fields = ["order__title", "provider__user_profile__user__first_name"]
    ordering_fields = ["assigned_at", "start_date"]
    ordering = ["-assigned_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        return OrderAssignment.objects.all().select_related(
            "order__client__user_profile", "provider__user_profile", "accepted_bid"
        )


class OrderAssignmentDetailApiView(StandardizedViewMixin, generics.RetrieveUpdateAPIView):
    serializer_class = OrderAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return OrderAssignment.objects.filter(
            provider__user_profile__user=user,
        ).select_related("order__client__user_profile", "provider__user_profile", "accepted_bid")


class MyAssignmentsView(StandardizedViewMixin, generics.ListAPIView):
    """Get current user's assignments (as provider)."""
    serializer_class = OrderAssignmentSerializer
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["order__status"]
    search_fields = ["order__title", "order__client__user_profile__user__first_name"]
    ordering_fields = ["assigned_at", "start_date"]
    ordering = ["-assigned_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return OrderAssignment.objects.filter(
            provider__user_profile__user=user
        ).select_related("order__client__user_profile", "provider__user_profile", "accepted_bid")


class MyOrderAssignmentsView(StandardizedViewMixin, generics.ListAPIView):
    """Get assignments for current user's orders (as client)."""
    serializer_class = OrderAssignmentSerializer
    permission_classes = [IsAuthenticated, HasClientProfile]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["provider", "order__status"]
    search_fields = ["order__title", "provider__user_profile__user__first_name"]
    ordering_fields = ["assigned_at", "start_date"]
    ordering = ["-assigned_at"]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return OrderAssignment.objects.filter(
            order__client__user_profile__user=user
        ).select_related("order__client__user_profile", "provider__user_profile", "accepted_bid")


# NEW ENDPOINTS FOR MOBILE APP FEATURES

class UpdateOrderStatusAPIView(StandardizedViewMixin, APIView):
    """Update order status (assigned → in_progress → completed)."""
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """Update order status."""
        try:
            order = get_object_or_404(Order, pk=pk)
            new_status = request.data.get('status')
            
            # Validate status transition
            valid_transitions = {
                'assigned': ['in_progress'],
                'in_progress': ['completed'],
            }
            
            if order.status not in valid_transitions:
                return Response(
                    {'error': f'Cannot update status from {order.status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if new_status not in valid_transitions[order.status]:
                return Response(
                    {'error': f'Invalid status transition from {order.status} to {new_status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update status and timestamps
            order.status = new_status
            if new_status == 'in_progress':
                order.started_at = timezone.now()
            elif new_status == 'completed':
                order.completed_at = timezone.now()
            
            order.save()
            
            return Response({
                'message': f'Order status updated to {new_status}',
                'status': order.status,
                'updated_at': order.updated_at
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to update order status: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CompleteOrderAPIView(StandardizedViewMixin, APIView):
    """Complete order with photos and client rating."""
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        """Complete order with completion photos and client rating."""
        try:
            order = get_object_or_404(Order, pk=pk)
            
            # Check if user is assigned to this order
            assignment = get_object_or_404(
                OrderAssignment,
                order=order,
                provider__user_profile__user=request.user
            )
            
            if order.status != 'in_progress':
                return Response(
                    {'error': 'Order must be in progress to complete'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update order status
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()
            
            # Handle completion photos
            completion_photos = request.FILES.getlist('completion_photos')
            for photo in completion_photos:
                OrderAttachment.objects.create(
                    file_name=photo.name,
                    file_type='image',
                    file_size=photo.size,
                    file_url=photo.url if hasattr(photo, 'url') else '',
                    mime_type=photo.content_type,
                    description='Completion photo',
                    uploaded_by=request.user
                )
            
            # Handle client rating
            client_rating = request.data.get('client_rating')
            client_review = request.data.get('client_review', '')
            
            if client_rating:
                assignment.client_rating = int(client_rating)
                assignment.client_review = client_review
                assignment.save()
            
            return Response({
                'message': 'Order completed successfully',
                'status': order.status,
                'completed_at': order.completed_at,
                'photos_uploaded': len(completion_photos)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to complete order: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UploadOrderAttachmentsAPIView(StandardizedViewMixin, APIView):
    """Upload attachments to order (before photos)."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        """Upload attachments to order."""
        try:
            order = get_object_or_404(Order, pk=pk)
            
            # Check permissions (client or assigned provider)
            can_upload = (
                order.client.user_profile.user == request.user or
                OrderAssignment.objects.filter(
                    order=order,
                    provider__user_profile__user=request.user
                ).exists()
            )
            
            if not can_upload:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Handle file uploads
            attachments = request.FILES.getlist('attachments')
            uploaded_files = []
            
            for attachment in attachments:
                order_attachment = OrderAttachment.objects.create(
                    file_name=attachment.name,
                    file_type=attachment.content_type.split('/')[0],
                    file_size=attachment.size,
                    file_url=attachment.url if hasattr(attachment, 'url') else '',
                    mime_type=attachment.content_type,
                    description=request.data.get('description', ''),
                    uploaded_by=request.user
                )
                
                # Add to order
                order.attachments.add(order_attachment)
                uploaded_files.append({
                    'id': order_attachment.id,
                    'file_name': order_attachment.file_name,
                    'file_type': order_attachment.file_type,
                    'file_size': order_attachment.file_size
                })
            
            return Response({
                'message': f'Uploaded {len(uploaded_files)} attachments',
                'attachments': uploaded_files
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to upload attachments: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetOrderAttachmentsAPIView(StandardizedViewMixin, generics.ListAPIView):
    """Get order attachments."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Get order attachments."""
        try:
            order = get_object_or_404(Order, pk=pk)
            
            # Check permissions
            can_view = (
                order.client.user_profile.user == request.user or
                OrderAssignment.objects.filter(
                    order=order,
                    provider__user_profile__user=request.user
                ).exists()
            )
            
            if not can_view:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            attachments = order.attachments.all()
            attachments_data = [{
                'id': att.id,
                'file_name': att.file_name,
                'file_type': att.file_type,
                'file_size': att.file_size,
                'file_url': att.file_url,
                'mime_type': att.mime_type,
                'description': att.description,
                'uploaded_by': att.uploaded_by.username,
                'created_at': att.created_at
            } for att in attachments]
            
            return Response({
                'attachments': attachments_data,
                'count': len(attachments_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get attachments: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RateClientAPIView(StandardizedViewMixin, APIView):
    """Rate client after job completion."""
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]

    def post(self, request, pk):
        """Rate client."""
        try:
            order = get_object_or_404(Order, pk=pk)
            
            # Check if user is assigned to this order
            assignment = get_object_or_404(
                OrderAssignment,
                order=order,
                provider__user_profile__user=request.user
            )
            
            if order.status != 'completed':
                return Response(
                    {'error': 'Order must be completed to rate client'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            rating = request.data.get('rating')
            review = request.data.get('review', '')
            
            if not rating or not (1 <= int(rating) <= 5):
                return Response(
                    {'error': 'Rating must be between 1 and 5'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            assignment.client_rating = int(rating)
            assignment.client_review = review
            assignment.save()
            
            return Response({
                'message': 'Client rated successfully',
                'rating': assignment.client_rating,
                'review': assignment.client_review
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to rate client: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StartWorkAPIView(StandardizedViewMixin, APIView):
    """Start work on assigned order."""
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]

    def post(self, request, pk):
        """Start work on order."""
        try:
            order = get_object_or_404(Order, pk=pk)
            
            # Check if user is assigned to this order
            assignment = get_object_or_404(
                OrderAssignment,
                order=order,
                provider__user_profile__user=request.user
            )
            
            if order.status != 'assigned':
                return Response(
                    {'error': 'Order must be assigned to start work'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update order status
            order.status = 'in_progress'
            order.started_at = timezone.now()
            order.save()
            
            # Update assignment
            assignment.start_date = timezone.now().date()
            assignment.start_time = timezone.now().time()
            assignment.save()
            
            return Response({
                'message': 'Work started successfully',
                'status': order.status,
                'started_at': order.started_at
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to start work: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetOrderAssignmentAPIView(StandardizedViewMixin, generics.RetrieveAPIView):
    """Get order assignment details."""
    serializer_class = OrderAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        order_id = self.kwargs['pk']
        order = get_object_or_404(Order, pk=order_id)
        
        # Check permissions
        can_view = (
            order.client.user_profile.user == self.request.user or
            OrderAssignment.objects.filter(
                order=order,
                provider__user_profile__user=self.request.user
            ).exists()
        )
        
        if not can_view:
            raise ValidationError('Permission denied')
        
        return get_object_or_404(OrderAssignment, order=order)