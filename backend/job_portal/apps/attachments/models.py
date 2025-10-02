import logging
import mimetypes
import os
import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils.abstract_models import AbstractTimestampedModel

UserModel = get_user_model()


def generic_attachment_storage_upload_to(instance, filename):
    """Generate upload path for generic attachments."""
    current_datetime = timezone.now().strftime("%Y/%m/%d")

    # Generate a unique identifier for the file
    unique_id = uuid.uuid4().hex[:8]
    updated_filename = f"{current_datetime}_{unique_id}_{filename}"

    # Get content type info for folder organization
    content_type = instance.content_type.model if instance.content_type else "generic"
    object_id = instance.object_id or "unknown"

    return f"attachments/{content_type}/{object_id}/{updated_filename}"


class Attachment(AbstractTimestampedModel):
    """Generic attachment model that can be linked to any model using ContentType."""

    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # File information
    file = models.FileField(_("File"), upload_to=generic_attachment_storage_upload_to)
    original_filename = models.CharField(_("Original Filename"), max_length=255)
    size = models.PositiveIntegerField(_("File Size (bytes)"))
    file_type = models.CharField(_("File Type"), max_length=100, blank=True)
    mime_type = models.CharField(_("MIME Type"), max_length=100, blank=True)

    # Upload information
    uploaded_by = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="uploaded_attachments",
        verbose_name=_("Uploaded By"),
    )

    # Additional metadata
    description = models.TextField(_("Description"), blank=True)
    is_public = models.BooleanField(_("Is Public"), default=True)

    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["uploaded_by", "created_at"]),
            models.Index(fields=["file_type"]),
        ]

    def save(self, *args, **kwargs):
        """Override save to automatically populate fields if not set."""
        if self.file and not self.original_filename:
            self.original_filename = os.path.basename(self.file.name)

        if self.file and not self.size:
            try:
                self.size = self.file.size
            except (OSError, AttributeError):
                self.size = 0

        if self.file and not self.mime_type:
            # Get MIME type from file extension
            mime_type, _ = mimetypes.guess_type(
                self.original_filename or self.file.name
            )
            if mime_type:
                self.mime_type = mime_type

        if self.file and not self.file_type:
            # Determine file type based on MIME type or extension
            if self.mime_type:
                if self.mime_type.startswith("image/"):
                    self.file_type = "image"
                elif self.mime_type.startswith("video/"):
                    self.file_type = "video"
                elif self.mime_type.startswith("audio/"):
                    self.file_type = "audio"
                elif self.mime_type in ["application/pdf"]:
                    self.file_type = "pdf"
                elif self.mime_type in [
                    "application/msword",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ]:
                    self.file_type = "document"
                elif self.mime_type in [
                    "application/vnd.ms-excel",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ]:
                    self.file_type = "spreadsheet"
                else:
                    self.file_type = "file"
            else:
                # Fallback to file extension
                ext = os.path.splitext(self.original_filename or self.file.name)[
                    1
                ].lower()
                if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
                    self.file_type = "image"
                elif ext in [".mp4", ".avi", ".mov", ".wmv", ".flv"]:
                    self.file_type = "video"
                elif ext in [".mp3", ".wav", ".flac", ".aac"]:
                    self.file_type = "audio"
                elif ext in [".pdf"]:
                    self.file_type = "pdf"
                elif ext in [".doc", ".docx"]:
                    self.file_type = "document"
                elif ext in [".xls", ".xlsx"]:
                    self.file_type = "spreadsheet"
                else:
                    self.file_type = "file"

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to clean up files from storage."""
        # Store file path before deletion
        file_path = self.file.path if self.file else None

        # Call parent delete method
        super().delete(*args, **kwargs)

        # Clean up file from storage
        if file_path and default_storage.exists(file_path):
            try:
                default_storage.delete(file_path)
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to delete file {file_path}: {e}")

    def __str__(self):
        return f"Attachment: {self.original_filename} for {self.content_type.model} #{self.object_id} [#{self.id}]"


def create_attachments(files, user, instance):
    """
    Create one or multiple attachments linked to a generic instance.

    :param files: list or QueryDict of uploaded files
    :param user: request.user (uploader)
    :param instance: model instance (Job, JobAssignment, Dispute, etc.)
    :return: list of Attachment objects
    """
    content_type = ContentType.objects.get_for_model(instance.__class__)
    attachments = []
    for file in files:
        attachment = Attachment.objects.create(
            file=file,
            uploaded_by=user,
            content_type=content_type,
            object_id=instance.id
        )
        attachments.append(attachment)
    return attachments
