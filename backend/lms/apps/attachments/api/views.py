from django.contrib.contenttypes.models import ContentType
from django_filters import ModelChoiceFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from lms.apps.attachments.models import Attachment
from lms.apps.core.utils.crud_base.views import BaseListApiView
from .serializers import BaseAttachmentSerializer


class BaseAttachmentListAPIView(BaseListApiView):
    search_fields = ["name", "id"]
    ordering_fields = ["id", "created_at", "updated_at"]

    class AttachmentFilter(FilterSet):
        content_type = ModelChoiceFilter(
            field_name="content_type",
            queryset=ContentType.objects.all(),
            to_field_name="model",
            label="Content Type",
        )
        NumberFilter(
            field_name="object_id",
            lookup_expr="exact",
        )

        class Meta:
            model = Attachment
            fields = ["id", "content_type", "object_id"]

    filterset_class = AttachmentFilter

    def get_queryset(self):
        return Attachment.objects.all()

    def get_serializer_class(self):
        return BaseAttachmentSerializer


class AttachmentListAPIView(BaseAttachmentListAPIView):
    pass
