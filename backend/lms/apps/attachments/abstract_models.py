from django.db import models
from django.utils.translation import gettext_lazy as _
from .utils import get_default_upload_file_name


class AbstractFileModel(models.Model):
    name = models.CharField(_("Name"), blank=True, max_length=100)
    original_name = models.CharField(
        _("Original Name"), blank=True, max_length=100, editable=False
    )
    file_type = models.CharField(_("File Type"), default="file", max_length=20)
    extension = models.CharField(_("Extension"), blank=True, max_length=100)
    alt = models.CharField(_("Alt"), blank=True, max_length=255)
    url = models.URLField(_("URL"), blank=True, max_length=255)
    size = models.CharField(_("Size"), blank=True, max_length=100)
    parent = models.BigIntegerField(_("Parent"), blank=True, null=True)
    file = models.FileField(
        _("File"), upload_to=get_default_upload_file_name, null=True, blank=True
    )
    storage_engine = models.CharField(
        _("Storage Engine"), max_length=20, default="local"
    )

    class Meta:
        abstract = True
        ordering = ("-id",)
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")

    def __str__(self):
        return f"self.name [#{self.pk}]"

    def get_alt(self):
        if self.alt:
            return self.alt
        return self.name

    def delete_file(self, *args, **kwargs):
        """Delete the file from storage when the model instance is deleted."""
        if self.file:
            self.file.delete(save=False)
