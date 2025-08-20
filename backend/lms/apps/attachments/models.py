import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from lms.apps.attachments.abstract_models import AbstractFileModel
from lms.apps.core.utils.abstract_models import AbstractTimestampedModel, models


class AttachmentManager(models.Manager):
    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id, object_id=obj.pk)


class Attachment(AbstractFileModel, AbstractTimestampedModel):
    attachment_type = models.CharField(max_length=20)
    content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    content_object = GenericForeignKey("content_type", "object_id")

    def save(self, *args, **kwargs) -> None:
        if self.file:
            self.original_name = self.file.name
            self.name = os.path.basename(self.file.name)
            self.extension = os.path.splitext(self.name)[1]
            self.size = self.file.size
        super().save(*args, **kwargs)

    objects = AttachmentManager()
