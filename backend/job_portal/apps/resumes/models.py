from django.contrib.auth import get_user_model
from django.db import models

from job_portal.apps.users.models import Master
from utils.abstract_models import TitleField, AbstractTimestampedModel

UserModel = get_user_model()


class ResumeStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class MasterResume(AbstractTimestampedModel):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, null=True, blank=True)
    title = TitleField()
    content = models.TextField()
    status = models.CharField(max_length=20, choices=ResumeStatus.choices, default=ResumeStatus.DRAFT)

    def __str__(self):
        return f"Resume: {self.title} [#{self.id}]"
