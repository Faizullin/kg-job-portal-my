from lms.apps.attachments.utils import get_default_upload_file_name
from django_filters import CharFilter, NumberFilter, BaseInFilter
from django_filters.rest_framework import FilterSet
from rest_framework import generics
from rest_framework.exceptions import ValidationError
import mimetypes
from pathlib import Path
from lms.apps.resources.models import VimeoUrlCacheModel, TemplateComponent
from lms.apps.attachments.api.serializers import BaseAttachmentSerializer
from lms.apps.attachments.models import Attachment
from lms.apps.core.utils.crud_base.views import (
    BaseApiViewSet,
    BaseListApiView,
    AuthControlMixin,
)
from lms.apps.core.utils.exceptions import StandardizedViewMixin
from .action_views import *  # noqa
from .serializers import MediaLibAttachmentUploadSerializer, VimeoUrlCacheSerializer
from .serializers import TemplateComponentSerializer


class NumberInFilter(BaseInFilter, NumberFilter):
    """Filter for multiple numeric values"""

    pass


class TemplateComponentApiViewSet(BaseApiViewSet):
    """
    ViewSet for managing Template Components.
    """

    search_fields = ["title", "component_type"]

    class TemplateComponentFilter(FilterSet):
        title = CharFilter(lookup_expr="icontains")
        ids = NumberInFilter(field_name="id", lookup_expr="in")

        class Meta:
            model = TemplateComponent
            fields = ["id", "title", "component_type", "is_active", "ids"]

    filterset_class = TemplateComponentFilter

    def get_queryset(self):
        return TemplateComponent.objects.all()

    def get_serializer_class(self):
        return TemplateComponentSerializer


class MediaLibAttachmentListApiView(BaseListApiView):
    """
    ViewSet for managing Media Library Attachments.
    """

    serializer_class = BaseAttachmentSerializer
    search_fields = ["name", "file_type"]

    class MediaLibAttachmentFilter(FilterSet):
        title = CharFilter(lookup_expr="icontains")

        class Meta:
            model = Attachment
            fields = ["id", "name", "file_type"]

    filterset_class = MediaLibAttachmentFilter

    def get_queryset(self):
        return Attachment.objects.all()


class MediaLibAttachmentDetailDestroyApiView(
    AuthControlMixin, StandardizedViewMixin, generics.RetrieveDestroyAPIView
):
    """ViewSet for retrieving and deleting Media Library Attachments."""

    serializer_class = BaseAttachmentSerializer

    def get_queryset(self):
        return Attachment.objects.all()


class MediaLibAttachmentUploadApiView(BaseApiView):
    ALLOWED_FORMATS = {
        "image": ["image/jpeg", "image/png", "image/gif", "image/webp"],
        "audio": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/flac"],
        "file": ["application/pdf", "application/msword", "text/plain"],
    }
    SIZE_LIMITS = {
        "image": 5 * 1024 * 1024,
        "audio": 50 * 1024 * 1024,
        "file": 25 * 1024 * 1024,
    }

    def _detect_file_type(self, file):
        """Detect file type and validate"""
        mime_type, _ = mimetypes.guess_type(file.name)
        ext = Path(file.name).suffix.lower()

        # Detect type
        for file_type, mime_types in self.ALLOWED_FORMATS.items():
            if mime_type in mime_types:
                detected_type = file_type
                break
        else:
            # Fallback to extension
            if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                detected_type = "image"
            elif ext in [".mp3", ".wav", ".ogg", ".flac"]:
                detected_type = "audio"
            else:
                detected_type = "file"

        # Validate size
        max_size = self.SIZE_LIMITS.get(detected_type, self.SIZE_LIMITS["file"])
        if file.size > max_size:
            size_mb = max_size // (1024 * 1024)
            raise ValidationError(
                f"{detected_type.title()} files must be under {size_mb}MB"
            )

        return detected_type

    def post(self, request, *args, **kwargs):
        """
        Handle file upload for media library attachments.
        """
        serializer = MediaLibAttachmentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post_id = serializer.validated_data.get("post_id")
        uploaded_file = serializer.validated_data.get("file")
        try:
            post_obj = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise ValidationError("Post not found")
        except Exception as e:
            raise ValidationError(e)
        if post_obj.post_type != "editor3":
            raise ValidationError("Post must be editor3")
        file_type = self._detect_file_type(uploaded_file)
        new_attachment_obj = Attachment.objects.create(
            file=serializer.validated_data["file"],
            file_type=file_type,
            attachment_type="file",
            storage_engine="protected-local",
        )
        new_file_url = request.build_absolute_uri(new_attachment_obj.file.url)
        new_attachment_obj.url = new_file_url
        new_attachment_obj.save()
        post_obj.attachments.add(new_attachment_obj)
        post_obj.save()
        return Response(BaseAttachmentSerializer(new_attachment_obj).data, status=201)


class VimeoUrlCacheApiViewSet(BaseApiViewSet):
    """
    ViewSet for managing Vimeo URL Cache.
    """

    search_fields = ["vimeo_link", "playable_video_link"]
    
    class VimeoUrlCacheModelFilter(FilterSet):
        vimeo_link = CharFilter(lookup_expr="icontains")
        playable_video_link = CharFilter(lookup_expr="icontains")

        class Meta:
            model = VimeoUrlCacheModel
            fields = ["id", "vimeo_link", "playable_video_link"]
    
    filterset_class = VimeoUrlCacheModelFilter

    def get_queryset(self):
        return VimeoUrlCacheModel.objects.all()

    def get_serializer_class(self):
        return VimeoUrlCacheSerializer
    
