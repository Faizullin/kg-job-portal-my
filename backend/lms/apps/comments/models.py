from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from lms.apps.core.utils.abstract_models import AbstractTimestampedModel, models

UserModel = get_user_model()


class Comment(AbstractTimestampedModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name="comments")
    user_name = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    text = models.TextField()
    meta_term = models.CharField(
        max_length=50,
        choices=[
            ("user_feedback", "User Feedback"),
            ("todo", "TODO"),
            ("notification", "Notification"),
        ],
        default="user_feedback"
    )

    def __str__(self):
        return '{}) {}'.format(self.pk, self.user)
