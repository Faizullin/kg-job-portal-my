from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel
from accounts.models import UserModel


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
        return f"Review by {self.reviewer.name} for {self.provider.user_profile.user.name} - {self.overall_rating}★ [#{self.id}]"
    
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
    """App feedback and rating from users."""
    
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='app_feedback')
    
    # Rating options (from screen 7)
    rating_options = models.JSONField(_("Rating Options"), default=list, help_text="Selected rating options from predefined list")
    
    # Detailed feedback (from screen 8)
    detailed_feedback = models.TextField(_("Detailed Feedback"), blank=True)
    
    # App version info
    app_version = models.CharField(_("App Version"), max_length=20, blank=True)
    device_info = models.CharField(_("Device Info"), max_length=100, blank=True)
    
    # Status
    is_processed = models.BooleanField(_("Processed"), default=False)
    admin_notes = models.TextField(_("Admin Notes"), blank=True)
    
    class Meta:
        verbose_name = _("App Feedback")
        verbose_name_plural = _("App Feedback")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback from {self.user.name} - {self.created_at.strftime('%Y-%m-%d')}... [#{self.id}]"