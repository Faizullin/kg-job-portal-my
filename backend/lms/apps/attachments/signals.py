from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from .models import Attachment


@receiver(pre_delete, sender=Attachment)
def pre_delete_files(sender, instance: Attachment, *args, **kwargs):
    try:
        instance.delete_file()
    except:
        pass


@receiver(pre_save, sender=Attachment)
def pre_save_files(sender, instance: Attachment, *args, **kwargs):
    if instance.pk:
        try:
            old_instance: Attachment = sender.objects.get(pk=instance.pk)
            if old_instance.file != instance.file and instance.file:
                old_instance.delete_file()
        except sender.DoesNotExist:
            pass
