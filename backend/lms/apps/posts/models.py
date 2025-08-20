from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from lms.apps.attachments.models import Attachment
from lms.apps.core.models import PublicationStatus
from lms.apps.core.utils.abstract_models import AbstractMetaModel, AbstractSlugModel, AbstractTimestampedModel

UserModel = get_user_model()


class Category(AbstractTimestampedModel, AbstractSlugModel):
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), max_length=1023)
    term = models.CharField(max_length=50, null=True, default=None)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return '{}) {}'.format(self.pk, self.title)


class Tag(AbstractTimestampedModel, AbstractSlugModel):
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), max_length=1023)
    term = models.CharField(max_length=50, null=True, default=None)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return '{}) {}'.format(self.pk, self.title)


class PostManager(models.Manager):
    def posts_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id, object_id=obj.pk)


class Post(AbstractTimestampedModel, AbstractMetaModel, AbstractSlugModel):
    objects = PostManager()

    title = models.CharField(_("Title"), max_length=200)
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)
    content = models.TextField()
    publication_status = models.IntegerField(
        choices=PublicationStatus.choices, default=PublicationStatus.DRAFT)
    post_type = models.CharField(_("Post Type"), max_length=20)

    attachments = GenericRelation(Attachment)
    thumbnail = models.ForeignKey(
        Attachment, null=True, blank=True, on_delete=models.SET_NULL,
    )
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True, )
    content_object = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} [#{self.pk}]"
