from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, generics
from rest_framework import permissions, viewsets, filters, status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.apps.core.utils.exceptions import StandardizedViewMixin


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class AuthControlMixin:
    authentication_classes = (TokenAuthentication, SessionAuthentication,)
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser,
    ]


class BaseListApiView(AuthControlMixin, StandardizedViewMixin, generics.ListAPIView):
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


class BaseApiViewSet(AuthControlMixin, StandardizedViewMixin, viewsets.ModelViewSet):
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


class BaseApiView(AuthControlMixin, StandardizedViewMixin, APIView):
    pass
