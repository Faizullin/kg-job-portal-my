import os
from django.apps import apps
from django.conf import settings
from django.db.models.fields.files import FileField


def collect():
    """
    Returns a dictionary with orphaned files from MEDIA_ROOT and PROTECTED_MEDIA_ROOT.
    {
        'media': [...],
        'protected': [...]
    }
    """

    def collect_files_on_disk(base_path):
        files_on_disk = set()
        for root, _, files in os.walk(base_path):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_path)
                files_on_disk.add(rel_path)
        return files_on_disk

    def collect_referenced_files():
        referenced = set()
        for model in apps.get_models():
            for field in model._meta.get_fields():
                if isinstance(field, FileField):
                    for instance in model.objects.all().only(field.name).iterator():
                        file_field = getattr(instance, field.name)
                        if file_field and file_field.name:
                            referenced.add(file_field.name)
        return referenced

    # Collect from MEDIA_ROOT
    media_root = settings.MEDIA_ROOT
    media_files = collect_files_on_disk(media_root)

    # Collect from PROTECTED_MEDIA_ROOT if defined
    protected_root = settings.PROTECTED_MEDIA_ROOT
    protected_files = collect_files_on_disk(protected_root)

    # Referenced files across all FileFields
    referenced_files = collect_referenced_files()

    # Orphaned files
    orphaned_in_media = media_files - referenced_files
    orphaned_in_protected = protected_files - referenced_files

    return {
        "media": sorted(orphaned_in_media),
        "protected": sorted(orphaned_in_protected),
    }
