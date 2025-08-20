from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, generics
from rest_framework import permissions, viewsets, filters, status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.exceptions import StandardizedViewMixin


class CustomPagination(pagination.PageNumberPagination):
    """Custom pagination class with configurable page size."""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class AuthControlMixin:
    """Mixin for authentication and permission control."""
    authentication_classes = (TokenAuthentication, SessionAuthentication,)
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser,
    ]


class AbstractBaseListApiView(AuthControlMixin, StandardizedViewMixin, generics.ListAPIView):
    """Base list API view with common functionality."""
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    ordering_fields = ["id", "created_at", "updated_at"]
    ordering = ["-id"]
    filterset_class = None

    def list(self, request, *args, **kwargs):
        if request.GET.get("disablePagination", None) is not None:
            self.pagination_class = None

        return super().list(request, *args, **kwargs)


class AbstractBaseApiViewSet(AuthControlMixin, StandardizedViewMixin, viewsets.ModelViewSet):
    """Base API viewset with common functionality."""
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    ordering_fields = ["id", "created_at", "updated_at"]
    ordering = ["-id"]
    filterset_class = None

    def list(self, request, *args, **kwargs):
        if request.GET.get("disablePagination", None) is not None:
            self.pagination_class = None

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        res = serializer.data
        if not "id" in res:
            res["id"] = new_obj.id
        return Response(res, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {
                "request": self.request,
                "view": self,
            }
        )
        return context


class AbstractBaseApiView(AuthControlMixin, StandardizedViewMixin, APIView):
    """Base API view with common functionality."""
    pass


class AbstractReadOnlyViewSet(AuthControlMixin, StandardizedViewMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for models that shouldn't be modified via API."""
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    ordering_fields = ["id", "created_at", "updated_at"]
    ordering = ["-id"]
    filterset_class = None


class PublicViewMixin:
    """Mixin for views that don't require authentication."""
    authentication_classes = ()
    permission_classes = [permissions.AllowAny]


class AbstractPublicApiView(PublicViewMixin, StandardizedViewMixin, APIView):
    """Public API view that doesn't require authentication."""
    pass


class AbstractPublicListApiView(PublicViewMixin, StandardizedViewMixin, generics.ListAPIView):
    """Public list API view that doesn't require authentication."""
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    ordering_fields = ["id", "created_at", "updated_at"]
    ordering = ["-id"]
    filterset_class = None


class AbstractSoftDeleteViewSet(AbstractBaseApiViewSet):
    """Viewset for models with soft delete functionality."""
    
    def get_queryset(self):
        """Filter out soft-deleted objects by default."""
        queryset = super().get_queryset()
        if hasattr(queryset.model, 'objects'):
            # Use the custom manager if available
            return queryset.model.objects.all()
        return queryset.filter(is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to implement soft delete."""
        instance = self.get_object()
        instance.delete()  # This will call the soft delete method
        return Response(status=status.HTTP_204_NO_CONTENT)


class AbstractAuditViewSet(AbstractBaseApiViewSet):
    """Viewset for models that need audit trail functionality."""
    
    def perform_create(self, serializer):
        """Set created_by field when creating objects."""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by field when updating objects."""
        serializer.save(updated_by=self.request.user)
