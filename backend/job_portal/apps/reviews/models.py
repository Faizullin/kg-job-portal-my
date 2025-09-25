from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel
from accounts.models import UserModel


class AppPlatform(models.TextChoices):
    ANDROID = 'android', _('Android')
    IOS = 'ios', _('iOS')
    WEB = 'web', _('Web')


class Review(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Simple reviews and ratings for service providers."""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='reviews_given')
    provider = models.ForeignKey('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='reviews_received')
    
    # Rating details
    overall_rating = models.PositiveIntegerField(
        _("Overall Rating"), 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Overall rating from 1 to 5 stars")
    )
    
    # Review content
    title = models.CharField(_("Review Title"), max_length=200, blank=True)
    comment = models.TextField(_("Review Comment"), blank=True)
    
    # Verification
    is_verified = models.BooleanField(_("Verified Review"), default=False)
    
    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        unique_together = ['order', 'reviewer']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.reviewer.name} for {self.provider.user_profile.user.username} - {self.overall_rating}★ [#{self.id}]"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update provider's average rating
        self.update_provider_rating()
    
    def update_provider_rating(self):
        """Update the provider's average rating and total reviews."""
        provider = self.provider
        reviews = Review.objects.filter(
            provider=provider,
        )
        
        if reviews.exists():
            avg_rating = reviews.aggregate(avg=models.Avg('overall_rating'))['avg']
            provider.average_rating = round(avg_rating, 2)
            provider.total_reviews = reviews.count()
        else:
            provider.average_rating = 0.00
            provider.total_reviews = 0
        
        provider.save(update_fields=['average_rating', 'total_reviews'])


class AppFeedback(AbstractTimestampedModel):
    """App feedback and rating system (from mobile UI screens 7-8)."""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='app_feedback')
    
    # General opinion checkboxes (from screen 7)
    general_opinion = models.JSONField(_("General Opinion"), default=dict, help_text=_("Selected options from checkboxes"))
    
    # Detailed feedback (from screen 8)
    detailed_feedback = models.TextField(_("Detailed Feedback"), blank=True, help_text=_("User's detailed experience description"))
    
    # Overall app rating
    overall_rating = models.PositiveIntegerField(
        _("Overall Rating"), 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Overall app rating from 1 to 5 stars")
    )
    
    # Feedback categories
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
        return f"App Feedback by {self.user.username} - {self.overall_rating}★ [#{self.id}]"
    
    def save(self, *args, **kwargs):
        """Auto-populate general_opinion based on checkbox fields."""
        if not self.general_opinion:
            self.general_opinion = {
                'everything_satisfies': self.everything_satisfies,
                'design_feedback': self.design_feedback,
                'usability_feedback': self.usability_feedback,
                'bug_report': self.bug_report,
                'missing_features': self.missing_features,
            }
        super().save(*args, **kwargs)

