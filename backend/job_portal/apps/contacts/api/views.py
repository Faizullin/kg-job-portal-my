from rest_framework import viewsets
from rest_framework.decorators import action, throttle_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from utils.helpers import get_client_ip

from ..models import SimpleContact
from .serializers import SimpleContactSerializer


class ContactCreateThrottle(ScopedRateThrottle):
    scope = "contact_create"

    def get_rate(self):
        return "5/hour"


class SimpleContactAPIViewSet(viewsets.ModelViewSet):
    """Contact enquiries API with minimal code."""

    queryset = SimpleContact.objects.all()
    serializer_class = SimpleContactSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == "create":
            permission_classes = []  # Allow anonymous contact creation
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:  # update, destroy
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter queryset with minimal validation."""
        queryset = super().get_queryset()

        enquiry_type = self.request.query_params.get("enquiry_type")
        if enquiry_type and enquiry_type in dict(
            SimpleContact.ContactEnquiryType.choices
        ):
            queryset = queryset.filter(enquiry_type=enquiry_type)

        user_id = self.request.query_params.get("user_id")
        if user_id:
            try:
                queryset = queryset.filter(user_id=int(user_id))
            except ValueError:
                pass  # Ignore invalid user_id

        return queryset.order_by("-created_at")

    @action(detail=False, methods=["get"])
    def enquiry_types(self, request):
        """Get available enquiry types."""
        return Response(
            {
                "enquiry_types": [
                    {"value": choice[0], "label": choice[1]}
                    for choice in SimpleContact.ContactEnquiryType.choices
                ]
            }
        )

    @throttle_classes([ContactCreateThrottle])
    def create(self, request, *args, **kwargs):
        """Create contact with throttling."""
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Create contact with IP tracking."""
        ip_address = get_client_ip(self.request)
        serializer.save(ip_address=ip_address)
