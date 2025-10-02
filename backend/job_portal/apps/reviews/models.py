from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _

from accounts.models import UserModel
from job_portal.apps.jobs.models import Job
from job_portal.apps.users.models import Master
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel, TitleField


class AppPlatform(models.TextChoices):
    ANDROID = 'android', _('Android')
    IOS = 'ios', _('iOS')
    WEB = 'web', _('Web')


class Review(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Simple review and rating system for masters."""

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='reviews_given')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='reviews_received')

    rating = models.PositiveIntegerField(
        _("Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    title = TitleField()
    comment = models.TextField(_("Review Comment"), blank=True)

    is_verified = models.BooleanField(_("Verified"), default=False)

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        unique_together = ['job', 'reviewer']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.master.user.username} - {self.rating}★ [#{self.id}]"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update provider's average rating
        self.update_provider_rating()

    def update_provider_rating(self):
        """Recalculate and update the average rating and total reviews for the provider."""

        master_statistics, created = self.master.statistics.get_or_create(master=self.master)
        reviews = Review.objects.filter(master=self.master)

        if reviews.exists():
            avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg']
            master_statistics.average_rating = round(avg_rating, 2)
            master_statistics.total_reviews = reviews.count()
        else:
            master_statistics.average_rating = 0.00
            master_statistics.total_reviews = 0

        master_statistics.save(update_fields=['average_rating', 'total_reviews'])


class AppFeedback(AbstractTimestampedModel):
    """Model to capture user feedback about the app experience."""

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='app_feedback')
    general_opinion = models.JSONField(_("General Opinion"), default=dict)
    detailed_feedback = models.TextField(_("Detailed Feedback"), blank=True,
                                         help_text=_("User's detailed experience description"))
    rating = models.PositiveIntegerField(
        _("Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    design_feedback = models.BooleanField(_("Excellent Design"), default=False)
    usability_feedback = models.BooleanField(_("Hard to Understand"), default=False)
    bug_report = models.BooleanField(_("App Problems"), default=False)
    missing_features = models.BooleanField(_("Missing Functions"), default=False)
    everything_satisfies = models.BooleanField(_("Everything Satisfies"), default=False)

    # Additional metadata
    app_version = models.CharField(_("App Version"), max_length=20, blank=True)
    device_info = models.CharField(_("Device Info"), max_length=100, blank=True)
    platform = models.CharField(_("Platform"), max_length=20, choices=AppPlatform.choices, blank=True)

    # Processing status
    is_reviewed = models.BooleanField(_("Reviewed by Admin"), default=False)
    admin_notes = models.TextField(_("Admin Notes"), blank=True)

    class Meta:
        verbose_name = _("App Feedback")
        verbose_name_plural = _("App Feedback")
        ordering = ['-created_at']

    def __str__(self):
        return f"App Feedback by {self.user.username} - {self.rating}★ [#{self.id}]"

    def save(self, *args, **kwargs):
        # Ensure general_opinion is populated based on individual feedback fields if not already set

        if not self.general_opinion:
            self.general_opinion = {
                'everything_satisfies': self.everything_satisfies,
                'design_feedback': self.design_feedback,
                'usability_feedback': self.usability_feedback,
                'bug_report': self.bug_report,
                'missing_features': self.missing_features,
            }
        super().save(*args, **kwargs)
