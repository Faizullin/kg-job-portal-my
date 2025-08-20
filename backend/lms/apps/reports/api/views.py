from django_filters import CharFilter
from django_filters.rest_framework import FilterSet
from rest_framework.decorators import action
from rest_framework.response import Response

from lms.apps.core.utils.crud_base.views import BaseApiViewSet
from lms.apps.posts.models import Post
from lms.apps.reports.api.serializers import LogReportSerializer, RecordPostSerializer
from lms.apps.reports.tasks import start_recording


class ReportViewSet(BaseApiViewSet):
    search_fields = [
        "title",
    ]

    class ReportFilter(FilterSet):
        title = CharFilter(lookup_expr="icontains")

        class Meta:
            model = Post
            fields = ["id", "title", "author", "publication_status"]

    filterset_class = ReportFilter

    def get_queryset(self):
        return (
            Post.objects.all()
            .filter(post_type="report")
            .prefetch_related(
                "author",
            )
        )

    def get_serializer_class(self):
        return RecordPostSerializer

    @action(
        methods=["post"],
        detail=False,
    )
    def record_start(self, request):
        name = request.data.get("name")
        if not name:
            return Response({"detail": "name is required"}, status=400)

        new_post_obj = start_recording(name, request.user.id)
        return Response(
            self.get_serializer(new_post_obj).data,
            status=200,
        )


class LogReportViewSet(BaseApiViewSet):
    search_fields = [
        "title",
    ]

    class LogReportFilter(FilterSet):
        title = CharFilter(lookup_expr="icontains")

        class Meta:
            model = Post
            fields = ["id", "title", "author", "publication_status"]

    filterset_class = LogReportFilter

    def get_queryset(self):
        return (
            Post.objects.all()
            .filter(post_type="log-report")
            .prefetch_related(
                "author",
            )
        )

    def get_serializer_class(self):
        return LogReportSerializer
