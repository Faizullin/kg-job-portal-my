from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractTimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-id"]


class AbstractMetaModel(models.Model):
    meta_title = models.CharField(_("Meta title"), blank=True, max_length=80)
    meta_keywords = models.CharField(_("Meta keywords"), blank=True, max_length=255)
    meta_description = models.TextField(_("Meta description"), blank=True)
    use_ssr = models.BooleanField(_("Use SSR"), default=False)
    render_url = models.CharField(_("Render URL"), blank=True, max_length=80)

    class Meta:
        abstract = True


class AbstractActiveModel(models.Model):
    is_active = models.BooleanField(_("Active"), default=False)

    class Meta:
        abstract = True


class AbstractSlugModel(models.Model):
    slug = models.CharField(_("Slug"), max_length=80, blank=True, unique=True)

    class Meta:
        abstract = True


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
