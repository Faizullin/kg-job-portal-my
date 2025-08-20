from django.db import models
from django.utils.translation import gettext_lazy as _


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

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Override delete to implement soft delete."""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save(update_fields=['deleted_at', 'is_deleted'])

    def restore(self, strict=True):
        """Restore a soft-deleted object."""
        from django.utils import timezone
        if strict and not self.is_deleted:
            raise ValueError("Object is not deleted")
        self.deleted_at = None
        self.restored_at = timezone.now()
        self.is_deleted = False
        self.save(update_fields=['deleted_at', 'restored_at', 'is_deleted'])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object."""
        super().delete(using, keep_parents)


def get_truncated_name(text: str, limit=25):
    """
    Truncate a string to a specified length, adding '...' if it exceeds the limit.

    Args:
        text (str): The string to truncate.
        limit (int): The maximum length of the string before truncation.

    Returns:
        str: The truncated string.
    """
    if len(text) > limit:
        return f"{text[:limit]}..."
    return text


def generate_slug(text: str, max_length=80):
    """
    Generate a URL-friendly slug from text.
    
    Args:
        text (str): The text to convert to a slug.
        max_length (int): Maximum length of the slug.
        
    Returns:
        str: The generated slug.
    """
    import re
    import unicodedata
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens and truncate
    slug = slug.strip('-')
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug
