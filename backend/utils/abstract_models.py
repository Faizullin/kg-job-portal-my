import re

from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.constants import LOOKUP_SEP
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.text import slugify
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


class AbstractSoftDeleteModel(models.Model):
    """Abstract model that provides soft delete functionality."""
    deleted_at = models.DateTimeField(_("Deleted at"), null=True, blank=True)
    restored_at = models.DateTimeField(_("Restored at"), null=True, blank=True)
    is_deleted = models.BooleanField(_("Is deleted"), default=False)

    # Use the custom manager by default
    # objects = SoftDeleteManager()

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


class TitleField(models.CharField):
    """Custom CharField for title with default max_length and verbose name."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 100)
        kwargs.setdefault('verbose_name', _("Title"))
        super().__init__(*args, **kwargs)

class UniqueFieldMixin:
    def check_is_bool(self, attrname):
        if not isinstance(getattr(self, attrname), bool):
            raise ValueError("'{}' argument must be True or False".format(attrname))

    @staticmethod
    def _get_fields(model_cls):
        return [
            (f, f.model if f.model != model_cls else None)
            for f in model_cls._meta.get_fields()
            if not f.is_relation or f.one_to_one or (f.many_to_one and f.related_model)
        ]

    def get_queryset(self, model_cls, slug_field):
        for field, model in self._get_fields(model_cls):
            if model and field == slug_field:
                return model._default_manager.all()
        return model_cls._default_manager.all()

    def find_unique(self, model_instance, field, iterator, *args):
        # exclude the current model instance from the queryset used in finding
        # next valid hash
        queryset = self.get_queryset(model_instance.__class__, field)
        if model_instance.pk:
            queryset = queryset.exclude(pk=model_instance.pk)

        # form a kwarg dict used to implement any unique_together constraints
        kwargs = {}
        for params in model_instance._meta.unique_together:
            if self.attname in params:
                for param in params:
                    kwargs[param] = getattr(model_instance, param, None)

        # for support django 2.2+
        query = Q()
        constraints = getattr(model_instance._meta, "constraints", None)
        if constraints:
            unique_constraints = filter(
                lambda c: isinstance(c, UniqueConstraint), constraints
            )
            for unique_constraint in unique_constraints:
                if self.attname in unique_constraint.fields:
                    condition = {
                        field: getattr(model_instance, field, None)
                        for field in unique_constraint.fields
                        if field != self.attname
                    }
                    query &= Q(**condition)

        new = next(iterator)
        kwargs[self.attname] = new
        while not new or queryset.filter(query, **kwargs):
            new = next(iterator)
            kwargs[self.attname] = new
        setattr(model_instance, self.attname, new)
        return new


class AutoSlugField(UniqueFieldMixin, models.SlugField):
    """Custom CharField for slug with default max_length and verbose name."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 80)
        kwargs.setdefault('verbose_name', _("Slug"))
        kwargs.setdefault('unique', True)
        kwargs.setdefault("editable", False)

        populate_from = kwargs.pop("populate_from", None)
        if populate_from is None:
            raise ValueError("missing 'populate_from' argument")
        else:
            self._populate_from = populate_from

        if not callable(populate_from):
            if not isinstance(populate_from, (list, tuple)):
                populate_from = (populate_from,)

            if not all(isinstance(e, str) for e in populate_from):
                raise TypeError(
                    "'populate_from' must be str or list[str] or tuple[str], found `%s`"
                    % populate_from
                )

        self.slugify_function = kwargs.pop("slugify_function", slugify)
        self.separator = kwargs.pop("separator", "-")
        self.overwrite = kwargs.pop("overwrite", False)
        self.overwrite_on_add = kwargs.pop("overwrite_on_add", True)
        self.allow_duplicates = kwargs.pop("allow_duplicates", False)
        self.max_unique_query_attempts = kwargs.pop(
            "max_unique_query_attempts", 100
        )
        super().__init__(*args, **kwargs)

    def _slug_strip(self, value):
        """
        Clean up a slug by removing slug separator characters that occur at
        the beginning or end of a slug.

        If an alternate separator is used, it will also replace any instances
        of the default '-' separator with the new separator.
        """
        re_sep = "(?:-|%s)" % re.escape(self.separator)
        value = re.sub("%s+" % re_sep, self.separator, value)
        return re.sub(r"^%s+|%s+$" % (re_sep, re_sep), "", value)

    @staticmethod
    def slugify_func(content, slugify_function):
        if content:
            return slugify_function(content)
        return ""

    def slug_generator(self, original_slug, start):
        yield original_slug
        for i in range(start, self.max_unique_query_attempts):
            slug = original_slug
            end = "%s%s" % (self.separator, i)
            end_len = len(end)
            if self.slug_len and len(slug) + end_len > self.slug_len:
                slug = slug[: self.slug_len - end_len]
                slug = self._slug_strip(slug)
            slug = "%s%s" % (slug, end)
            yield slug
        raise RuntimeError(
            "max slug attempts for %s exceeded (%s)"
            % (original_slug, self.max_unique_query_attempts)
        )

    def create_slug(self, model_instance, add):
        slug = getattr(model_instance, self.attname)
        use_existing_slug = False
        if slug and not self.overwrite:
            # Existing slug and not configured to overwrite - Short-circuit
            # here to prevent slug generation when not required.
            use_existing_slug = True

        if self.overwrite_on_add and add:
            use_existing_slug = False

        if use_existing_slug:
            return slug

        # get fields to populate from and slug field to set
        populate_from = self._populate_from
        if not isinstance(populate_from, (list, tuple)):
            populate_from = (populate_from,)

        slug_field = model_instance._meta.get_field(self.attname)
        slugify_function = getattr(
            model_instance, "slugify_function", self.slugify_function
        )

        # slugify the original field content and set next step to 2
        slug_for_field = lambda lookup_value: self.slugify_func(
            self.get_slug_fields(model_instance, lookup_value),
            slugify_function=slugify_function,
        )
        slug = self.separator.join(map(slug_for_field, populate_from))
        start = 2

        # strip slug depending on max_length attribute of the slug field
        # and clean-up
        self.slug_len = slug_field.max_length
        if self.slug_len:
            slug = slug[: self.slug_len]
        slug = self._slug_strip(slug)
        original_slug = slug

        if self.allow_duplicates:
            setattr(model_instance, self.attname, slug)
            return slug

        return self.find_unique(
            model_instance, slug_field, self.slug_generator(original_slug, start)
        )

    def get_slug_fields(self, model_instance, lookup_value):
        if callable(lookup_value):
            # A function has been provided
            return "%s" % lookup_value(model_instance)

        lookup_value_path = lookup_value.split(LOOKUP_SEP)
        attr = model_instance
        for elem in lookup_value_path:
            try:
                attr = getattr(attr, elem)
            except AttributeError:
                raise AttributeError(
                    "value {} in AutoSlugField's 'populate_from' argument {} returned an error - {} has no attribute {}".format(
                        # noqa: E501
                        elem, lookup_value, attr, elem
                    )
                )
        if callable(attr):
            return "%s" % attr()

        return attr

    def pre_save(self, model_instance, add):
        value = force_str(self.create_slug(model_instance, add))
        return value

    def get_internal_type(self):
        return "SlugField"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["populate_from"] = self._populate_from
        if not self.separator == "-":
            kwargs["separator"] = self.separator
        if self.overwrite is not False:
            kwargs["overwrite"] = True
        if self.allow_duplicates is not False:
            kwargs["allow_duplicates"] = True
        return name, path, args, kwargs


class AvailableField(models.BooleanField):
    """Custom BooleanField for availability with default verbose name and value."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', True)
        kwargs.setdefault('verbose_name', _("Available"))
        super().__init__(*args, **kwargs)


class ActiveField(models.BooleanField):
    """Custom BooleanField for active status with default verbose name and value."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', True)
        kwargs.setdefault('verbose_name', _("Active"))
        super().__init__(*args, **kwargs)


class AdvancedLocationField(models.CharField):
    """Custom CharField for advanced location with default max_length and verbose name."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 255)
        kwargs.setdefault('verbose_name', _("Location[Advanced]"))
        super().__init__(*args, **kwargs)


class PhoneNumberField(models.CharField):
    """Custom CharField for phone number with default max_length and verbose name."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 20)
        kwargs.setdefault('verbose_name', _("Phone Number"))
        super().__init__(*args, **kwargs)
