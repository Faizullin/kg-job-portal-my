import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage

from .models import Attachment

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Attachment)
def cleanup_attachment_file(sender, instance, **kwargs):
    """Clean up attachment file when Attachment instance is deleted."""
    if instance.file:
        try:
            if default_storage.exists(instance.file.name):
                default_storage.delete(instance.file.name)
                logger.info(f"Successfully deleted attachment file: {instance.file.name}")
        except Exception as e:
            logger.warning(f"Failed to delete attachment file {instance.file.name}: {e}")
