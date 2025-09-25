from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SoftDeleteManager(models.Manager):
    """
    Enhanced soft delete manager that automatically filters out soft-deleted objects.
    Provides comprehensive methods to work with both active and deleted objects.
    Eliminates the need for manual is_deleted=False filtering in views.
    """

    def get_queryset(self):
        """Return only non-deleted objects by default."""
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        """Return all objects including deleted ones."""
        return super().get_queryset()

    def deleted_only(self):
        """Return only deleted objects."""
        return super().get_queryset().filter(is_deleted=True)

    def restore(self, pk):
        """Restore a soft-deleted object by primary key."""
        obj = self.all_with_deleted().get(pk=pk)
        if obj.is_deleted:
            obj.restore()
        return obj

    def bulk_restore(self, pks):
        """Restore multiple soft-deleted objects by primary keys."""
        return self.all_with_deleted().filter(pk__in=pks, is_deleted=True).update(
            is_deleted=False,
            deleted_at=None,
            restored_at=timezone.now()
        )

    def bulk_soft_delete(self, pks):
        """Soft delete multiple objects by primary keys."""
        return self.filter(pk__in=pks).update(
            is_deleted=True,
            deleted_at=timezone.now()
        )

    def get_deleted_count(self):
        """Get count of deleted objects."""
        return self.deleted_only().count()

    def get_active_count(self):
        """Get count of active objects."""
        return self.count()


class CascadingSoftDeleteManager(SoftDeleteManager):
    """
    Advanced soft delete manager that can handle cascading soft deletes.
    Automatically soft deletes related objects when the main object is soft deleted.
    """

    def get_queryset(self):
        """Return only non-deleted objects by default."""
        return super().get_queryset().filter(is_deleted=False)

    def cascade_soft_delete(self, obj, cascade_fields=None):
        """
        Soft delete an object and optionally cascade to related objects.
        
        Args:
            obj: The object to soft delete
            cascade_fields: List of field names to cascade soft delete to
        """

        # Soft delete the main object
        obj.deleted_at = timezone.now()
        obj.is_deleted = True
        obj.save(update_fields=['deleted_at', 'is_deleted'])

        # Handle cascading if specified
        if cascade_fields:
            self._cascade_to_related_objects(obj, cascade_fields)

    def _cascade_to_related_objects(self, obj, cascade_fields):
        """Cascade soft delete to related objects."""

        for field_name in cascade_fields:
            if hasattr(obj, field_name):
                related_objects = getattr(obj, field_name)

                # Handle different types of relationships
                if hasattr(related_objects, 'all'):  # Many-to-many or reverse foreign key
                    for related_obj in related_objects.all():
                        if hasattr(related_obj, 'is_deleted'):
                            related_obj.deleted_at = timezone.now()
                            related_obj.is_deleted = True
                            related_obj.save(update_fields=['deleted_at', 'is_deleted'])

                elif hasattr(related_objects, 'is_deleted'):  # One-to-one or foreign key
                    related_objects.deleted_at = timezone.now()
                    related_objects.is_deleted = True
                    related_objects.save(update_fields=['deleted_at', 'is_deleted'])

    def restore_with_cascade(self, obj, cascade_fields=None):
        """
        Restore an object and optionally cascade restore to related objects.
        
        Args:
            obj: The object to restore
            cascade_fields: List of field names to cascade restore to
        """
        # Restore the main object
        obj.restore()

        # Handle cascading restore if specified
        if cascade_fields:
            self._cascade_restore_related_objects(obj, cascade_fields)

    def _cascade_restore_related_objects(self, obj, cascade_fields):
        """Cascade restore to related objects."""
        for field_name in cascade_fields:
            if hasattr(obj, field_name):
                related_objects = getattr(obj, field_name)

                # Handle different types of relationships
                if hasattr(related_objects, 'all'):  # Many-to-many or reverse foreign key
                    for related_obj in related_objects.all():
                        if hasattr(related_obj, 'is_deleted') and related_obj.is_deleted:
                            related_obj.restore()

                elif hasattr(related_objects, 'is_deleted') and related_objects.is_deleted:
                    related_objects.restore()


class AbstractTimestampedModel(models.Model):
    """Abstract model that provides created_at and updated_at timestamp fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-id"]


class AbstractMetaModel(models.Model):
    """Abstract model for SEO and meta information."""
    meta_title = models.CharField(_("Meta title"), blank=True, max_length=80)
    meta_keywords = models.CharField(_("Meta keywords"), blank=True, max_length=255)
    meta_description = models.TextField(_("Meta description"), blank=True)
    use_ssr = models.BooleanField(_("Use SSR"), default=False)
    render_url = models.CharField(_("Render URL"), blank=True, max_length=80)

    class Meta:
        abstract = True


class AbstractActiveModel(models.Model):
    """Abstract model that provides an is_active field for soft activation/deactivation."""
    is_active = models.BooleanField(_("Active"), default=False)

    class Meta:
        abstract = True


class AbstractSlugModel(models.Model):
    """Abstract model that provides a slug field for URL-friendly identifiers."""
    slug = models.CharField(_("Slug"), max_length=80, blank=True, unique=True)

    class Meta:
        abstract = True


class AbstractSoftDeleteModel(models.Model):
    """Abstract model that provides soft delete functionality."""
    deleted_at = models.DateTimeField(_("Deleted at"), null=True, blank=True)
    restored_at = models.DateTimeField(_("Restored at"), null=True, blank=True)
    is_deleted = models.BooleanField(_("Is deleted"), default=False)

    # Use the custom manager by default
    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Override delete to implement soft delete."""
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save(update_fields=['deleted_at', 'is_deleted'])

    def restore(self, strict=True):
        """Restore a soft-deleted object."""
        if strict and not self.is_deleted:
            raise ValueError("Object is not deleted")
        self.deleted_at = None
        self.restored_at = timezone.now()
        self.is_deleted = False
        self.save(update_fields=['deleted_at', 'restored_at', 'is_deleted'])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object."""
        super().delete(using, keep_parents)


class AbstractCascadingSoftDeleteModel(AbstractSoftDeleteModel):
    """
    Abstract model that provides cascading soft delete functionality.
    Automatically soft deletes related objects when this object is soft deleted.
    """

    # Use the cascading manager
    objects = CascadingSoftDeleteManager()

    class Meta:
        abstract = True

    def get_cascade_fields(self):
        """
        Override this method to specify which fields should cascade soft delete.
        Return a list of field names.
        """
        return []

    def delete(self, using=None, keep_parents=False):
        """Override delete to implement cascading soft delete."""
        cascade_fields = self.get_cascade_fields()
        if cascade_fields:
            self.objects.cascade_soft_delete(self, cascade_fields)
        else:
            super().delete(using, keep_parents)

    def restore(self, strict=True):
        """Override restore to implement cascading restore."""
        cascade_fields = self.get_cascade_fields()
        if cascade_fields:
            self.objects.restore_with_cascade(self, cascade_fields)
        else:
            super().restore(strict)
