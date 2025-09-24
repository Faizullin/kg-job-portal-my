from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel
from accounts.models import UserModel


class PricingStructure(AbstractTimestampedModel):
    """Pricing structure for service providers."""
    provider = models.ForeignKey('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='pricing_structures')
    service_subcategory = models.ForeignKey('core.ServiceSubcategory', on_delete=models.CASCADE, related_name='pricing_structures')
    
    # Pricing options
    hourly_rate = models.DecimalField(_("Hourly Rate"), max_digits=10, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(_("Daily Rate"), max_digits=10, decimal_places=2, null=True, blank=True)
    per_order_rate = models.DecimalField(_("Per Order Rate"), max_digits=10, decimal_places=2, null=True, blank=True)
    minimum_charge = models.DecimalField(_("Minimum Charge"), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Additional pricing info
    currency = models.CharField(_("Currency"), max_length=3, default='KGS')
    is_negotiable = models.BooleanField(_("Price Negotiable"), default=True)
    includes_materials = models.BooleanField(_("Includes Materials"), default=False)
    
    class Meta:
        verbose_name = _("Pricing Structure")
        verbose_name_plural = _("Pricing Structures")
        unique_together = ['provider', 'service_subcategory']
    
    def __str__(self):
        return f"{self.provider.user_profile.user.username} - {self.service_subcategory.name} Pricing"


class ProfessionalInformation(AbstractTimestampedModel):
    """Professional information for service providers."""
    provider = models.OneToOneField('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='professional_info')
    
    # Work experience
    years_of_experience = models.PositiveIntegerField(_("Years of Experience"), default=0)
    work_experience_description = models.TextField(_("Work Experience Description"), blank=True)
    
    # Education
    education_level = models.CharField(_("Education Level"), max_length=50, choices=[
        ('high_school', _('High School')),
        ('vocational', _('Vocational School')),
        ('bachelor', _('Bachelor Degree')),
        ('master', _('Master Degree')),
        ('phd', _('PhD')),
        ('other', _('Other')),
    ], blank=True)
    education_institution = models.CharField(_("Education Institution"), max_length=200, blank=True)
    education_field = models.CharField(_("Field of Study"), max_length=100, blank=True)
    graduation_year = models.PositiveIntegerField(_("Graduation Year"), null=True, blank=True)
    
    # Skills and certifications
    specializations = models.TextField(_("Specializations"), blank=True)
    tools_and_equipment = models.TextField(_("Tools and Equipment"), blank=True)
    
    class Meta:
        verbose_name = _("Professional Information")
        verbose_name_plural = _("Professional Information")
    
    def __str__(self):
        return f"{self.provider.user_profile.user.username} - Professional Info"


class Language(models.Model):
    """Languages spoken by service providers."""
    name = models.CharField(_("Language Name"), max_length=50, unique=True)
    code = models.CharField(_("Language Code"), max_length=5, unique=True)
    
    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProviderLanguage(models.Model):
    """Many-to-many relationship for provider languages."""
    provider = models.ForeignKey('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='languages')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='providers')
    proficiency_level = models.CharField(_("Proficiency Level"), max_length=20, choices=[
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
        ('native', _('Native')),
    ], default='intermediate')
    
    class Meta:
        verbose_name = _("Provider Language")
        verbose_name_plural = _("Provider Languages")
        unique_together = ['provider', 'language']
    
    def __str__(self):
        return f"{self.provider.user_profile.user.username} - {self.language.name} ({self.proficiency_level})"


class Certificate(models.Model):
    """Certificates and qualifications."""
    provider = models.ForeignKey('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='certificates')
    
    # Certificate details
    name = models.CharField(_("Certificate Name"), max_length=200)
    issuing_organization = models.CharField(_("Issuing Organization"), max_length=200)
    issue_date = models.DateField(_("Issue Date"))
    expiry_date = models.DateField(_("Expiry Date"), null=True, blank=True)
    certificate_number = models.CharField(_("Certificate Number"), max_length=100, blank=True)
    
    # File upload
    certificate_file = models.FileField(_("Certificate File"), upload_to='certificates/', null=True, blank=True)
    certificate_url = models.URLField(_("Certificate URL"), blank=True)
    
    # Verification
    is_verified = models.BooleanField(_("Verified"), default=False)
    verified_at = models.DateTimeField(_("Verified At"), null=True, blank=True)
    verified_by = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_certificates')
    
    class Meta:
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.provider.user_profile.user.username} - {self.name}"


class WorkPortfolio(AbstractTimestampedModel):
    """Portfolio of work examples for service providers."""
    provider = models.ForeignKey('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='portfolio_items')
    
    # Work details
    title = models.CharField(_("Work Title"), max_length=200)
    description = models.TextField(_("Work Description"))
    service_category = models.ForeignKey('core.ServiceSubcategory', on_delete=models.CASCADE, related_name='portfolio_items')
    
    # Media
    image = models.ImageField(_("Work Image"), upload_to='portfolio/images/', null=True, blank=True)
    image_url = models.URLField(_("Image URL"), blank=True)
    video_url = models.URLField(_("Video URL"), blank=True)
    
    # Work details
    completion_date = models.DateField(_("Completion Date"), null=True, blank=True)
    client_feedback = models.TextField(_("Client Feedback"), blank=True)
    is_featured = models.BooleanField(_("Featured Work"), default=False)
    
    # Privacy
    is_public = models.BooleanField(_("Public Portfolio"), default=True)
    
    class Meta:
        verbose_name = _("Work Portfolio")
        verbose_name_plural = _("Work Portfolios")
        ordering = ['-is_featured', '-completion_date', '-created_at']
    
    def __str__(self):
        return f"{self.provider.user_profile.user.username} - {self.title}"


class AvailabilityStatus(AbstractTimestampedModel):
    """Real-time availability status for service providers."""
    provider = models.OneToOneField('users.ServiceProviderProfile', on_delete=models.CASCADE, related_name='availability_status')
    
    # Status
    status = models.CharField(_("Current Status"), max_length=20, choices=[
        ('available', _('Available')),
        ('busy', _('Currently on Task')),
        ('offline', _('Offline')),
        ('break', _('On Break')),
    ], default='available')
    
    # Current task info
    current_order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='provider_status')
    estimated_completion = models.DateTimeField(_("Estimated Completion"), null=True, blank=True)
    
    # Location
    current_location = models.CharField(_("Current Location"), max_length=200, blank=True)
    is_location_accurate = models.BooleanField(_("Location Accurate"), default=False)
    last_location_update = models.DateTimeField(_("Last Location Update"), null=True, blank=True)
    
    # Working hours
    working_hours_start = models.TimeField(_("Working Hours Start"), null=True, blank=True)
    working_hours_end = models.TimeField(_("Working Hours End"), null=True, blank=True)
    working_days = models.JSONField(_("Working Days"), default=list)  # ['monday', 'tuesday', ...]
    
    class Meta:
        verbose_name = _("Availability Status")
        verbose_name_plural = _("Availability Statuses")
    
    def __str__(self):
        return f"{self.provider.user_profile.user.username} - {self.get_status_display()}"


class UserPreference(AbstractTimestampedModel):
    """User preferences for personalized recommendations."""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='preferences')
    
    # Service preferences
    preferred_categories = models.ManyToManyField('core.ServiceCategory', blank=True, related_name='user_preferences')
    preferred_subcategories = models.ManyToManyField('core.ServiceSubcategory', blank=True, related_name='user_preferences')
    
    # Provider preferences
    preferred_providers = models.ManyToManyField('users.ServiceProviderProfile', blank=True, related_name='preferred_by_users')
    blocked_providers = models.ManyToManyField('users.ServiceProviderProfile', blank=True, related_name='blocked_by_users')
    
    # Location preferences
    preferred_cities = models.JSONField(_("Preferred Cities"), default=list)
    max_distance_km = models.PositiveIntegerField(_("Max Distance (km)"), default=50)
    
    # Budget preferences
    budget_range_min = models.DecimalField(_("Budget Range Min"), max_digits=10, decimal_places=2, null=True, blank=True)
    budget_range_max = models.DecimalField(_("Budget Range Max"), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Quality preferences
    min_rating_preference = models.DecimalField(_("Minimum Rating Preference"), max_digits=3, decimal_places=2, default=3.0)
    prefer_verified_providers = models.BooleanField(_("Prefer Verified Providers"), default=True)
    
    class Meta:
        verbose_name = _("User Preference")
        verbose_name_plural = _("User Preferences")
    
    def __str__(self):
        return f"{self.user.username} - Preferences"


class RecommendationEngine(AbstractTimestampedModel):
    """Recommendation engine for personalized suggestions."""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='recommendations')
    
    # Recommendation type
    recommendation_type = models.CharField(_("Recommendation Type"), max_length=30, choices=[
        ('service_category', _('Service Category')),
        ('service_provider', _('Service Provider')),
        ('order_suggestion', _('Order Suggestion')),
        ('trending_service', _('Trending Service')),
    ])
    
    # Recommendation data
    recommended_object_type = models.CharField(_("Recommended Object Type"), max_length=50)
    recommended_object_id = models.PositiveIntegerField(_("Recommended Object ID"))
    
    # Recommendation metadata
    confidence_score = models.DecimalField(_("Confidence Score"), max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(1)])
    reason = models.CharField(_("Recommendation Reason"), max_length=200)
    algorithm_version = models.CharField(_("Algorithm Version"), max_length=20, default='v1.0')
    
    # User interaction
    is_viewed = models.BooleanField(_("Is Viewed"), default=False)
    is_clicked = models.BooleanField(_("Is Clicked"), default=False)
    is_dismissed = models.BooleanField(_("Is Dismissed"), default=False)
    viewed_at = models.DateTimeField(_("Viewed At"), null=True, blank=True)
    clicked_at = models.DateTimeField(_("Clicked At"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Recommendation")
        verbose_name_plural = _("Recommendations")
        ordering = ['-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'recommendation_type', 'confidence_score']),
            models.Index(fields=['recommended_object_type', 'recommended_object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_recommendation_type_display()} ({self.confidence_score})"


class StatisticsAggregation(AbstractTimestampedModel):
    """Aggregated statistics for dashboard and analytics."""
    date = models.DateField(_("Date"), unique=True)
    
    # Provider statistics
    total_providers = models.PositiveIntegerField(_("Total Providers"), default=0)
    active_providers = models.PositiveIntegerField(_("Active Providers"), default=0)
    verified_providers = models.PositiveIntegerField(_("Verified Providers"), default=0)
    average_provider_rating = models.DecimalField(_("Average Provider Rating"), max_digits=3, decimal_places=2, default=0.00)
    
    # Client statistics
    total_clients = models.PositiveIntegerField(_("Total Clients"), default=0)
    active_clients = models.PositiveIntegerField(_("Active Clients"), default=0)
    
    # Order statistics
    total_orders = models.PositiveIntegerField(_("Total Orders"), default=0)
    completed_orders = models.PositiveIntegerField(_("Completed Orders"), default=0)
    cancelled_orders = models.PositiveIntegerField(_("Cancelled Orders"), default=0)
    average_order_value = models.DecimalField(_("Average Order Value"), max_digits=10, decimal_places=2, default=0.00)
    
    # Review statistics
    total_reviews = models.PositiveIntegerField(_("Total Reviews"), default=0)
    average_review_rating = models.DecimalField(_("Average Review Rating"), max_digits=3, decimal_places=2, default=0.00)
    
    # Search statistics
    total_searches = models.PositiveIntegerField(_("Total Searches"), default=0)
    searches_with_results = models.PositiveIntegerField(_("Searches with Results"), default=0)
    
    class Meta:
        verbose_name = _("Statistics Aggregation")
        verbose_name_plural = _("Statistics Aggregations")
        ordering = ['-date']
    
    def __str__(self):
        return f"Statistics for {self.date}"
