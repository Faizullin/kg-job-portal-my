from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from utils.abstract_models import AbstractTimestampedModel, TitleField

UserModel = get_user_model()


class NotificationLevel(models.TextChoices):
    INFO = 'info', _('Info')
    WARNING = 'warning', _('Warning')
    ERROR = 'error', _('Error')


class Notification(AbstractTimestampedModel):
    """A model to represent user notifications."""

    title = TitleField()
    message = models.TextField(_("Message"))
    level = models.CharField(_("Level"), max_length=20, choices=NotificationLevel.choices,
                             default=NotificationLevel.INFO)

    recipient = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('recipient'),
        blank=False,
    )
    is_read = models.BooleanField(_("Read"), default=False)
    read_at = models.DateTimeField(_("Read At"), null=True, blank=True)

    verb = models.CharField(_('Verb'), max_length=255)
    actor_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notify_actor',
        verbose_name=_('actor content type')
    )
    actor_object_id = models.CharField(_('actor object id'), max_length=255)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notify_target',
        verbose_name=_('target content type'),
        blank=True,
        null=True
    )
    target_object_id = models.CharField(_('target object id'), max_length=255, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title}... [#{self.id}]"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    def mark_as_unread(self):
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save()

    # def qs_read(self):
    #     return self.filter(is_read=True)
    #
    # def qs_unread(self):
    #     return self.filter(is_read=False)
    #
    # def mark_all_as_read(self, recipient=None):
    #     """Mark as read any unread messages in the current queryset.
    #
    #     Optionally, filter these by recipient first.
    #     """
    #
    #     q_set = self.qs_unread()
    #     if recipient:
    #         q_set = q_set.filter(recipient=recipient)
    #
    #     return q_set.update(is_read=True)


def notify(verb: str, **kwargs):
    """
    Handler function to create Notification instance upon action signal call.
    """
    # Pull the options out of kwargs
    kwargs.pop('signal', None)
    recipient = kwargs.pop('recipient')
    actor = kwargs.pop('sender')
    optional_objs = [
        (kwargs.pop(opt, None), opt)
        for opt in ('target', 'action_object')
    ]
    level = kwargs.pop('level', NotificationLevel.INFO)
    actor_for_concrete_model = kwargs.pop('actor_for_concrete_model', True)

    # Check if User or Group
    if isinstance(recipient, Group):
        recipients = recipient.user_set.all()
    elif isinstance(recipient, (QuerySet, list)):
        recipients = recipient
    else:
        recipients = [recipient]

    new_notifications = []

    for recipient in recipients:
        new_notify = Notification(
            recipient=recipient,
            title=kwargs.pop('title', 'Notification'),
            message=kwargs.pop('message', ''),
            level=level,
            verb=str(verb),
            actor_content_type=ContentType.objects.get_for_model(actor, for_concrete_model=actor_for_concrete_model),
            actor_object_id=actor.pk,
        )

        # Set optional objects
        for obj, opt in optional_objs:
            if obj is not None:
                for_concrete_model = kwargs.pop(f'{opt}_for_concrete_model', True)
                setattr(new_notify, '%s_object_id' % opt, obj.pk)
                setattr(new_notify, '%s_content_type' % opt,
                        ContentType.objects.get_for_model(obj, for_concrete_model=for_concrete_model))

        new_notify.save()
        new_notifications.append(new_notify)

    return new_notifications
