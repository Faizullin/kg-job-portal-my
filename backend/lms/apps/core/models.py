from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusChoices(models.TextChoices):
    PENDING = 'Pending', _('Pending')
    ACCEPTED = 'Accepted', _('Accepted')
    REJECTED = 'Rejected', _('Rejected')
    IN_PROGRESS = 'In Progress', _('In Progress')
    PASS = 'Pass', _('Pass')
    FAIL = 'Fail', _('Fail')
    UPCOMING = 'Upcoming', _('Upcoming')
    COMPLETED = 'Completed', _('Completed')
    CANCELLED = 'Cancelled', _('Cancelled')


class PublicationStatus(models.IntegerChoices):
    DRAFT = 0, "Draft"
    PUBLISH = 1, "Publish"


class EventChoices(models.TextChoices):
    NEW = 'New', _('New')
    VALUE_CHANGE = 'Value Change', _('Value Change')
    AUTO_ASSIGN = 'Auto Assign', _('Auto Assign')


class DayChoices(models.TextChoices):
    SUNDAY = 'Sunday', _('Sunday')
    MONDAY = 'Monday', _('Monday')
    TUESDAY = 'Tuesday', _('Tuesday')
    WEDNESDAY = 'Wednesday', _('Wednesday')
    THURSDAY = 'Thursday', _('Thursday')
    FRIDAY = 'Friday', _('Friday')
    SATURDAY = 'Saturday', _('Saturday')
