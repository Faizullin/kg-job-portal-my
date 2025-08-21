from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel
from accounts.models import UserModel


class UserProfile(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Extended user profile for job portal functionality."""
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='job_portal_profile')
    user_type = models.CharField(_("User Type"), max_length=20, choices=[
        ('client', _('Client')),
        ('service_provider', _('Service Provider')),
        ('both', _('Both')),
    ], default='client')
    
    # Profile information
    bio = models.TextField(_("Bio"), blank=True)
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)
    gender = models.CharField(_("Gender"), max_length=10, choices=[
        ('male', _('Male')),
        ('female', _('Female')),
        ('other', _('Other')),
        ('prefer_not_to_say', _('Prefer not to say')),
    ], blank=True)
    
    # Contact information
    phone_number = models.CharField(_("Phone Number"), max_length=20, blank=True)
    address = models.TextField(_("Address"), blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    state = models.CharField(_("State/Province"), max_length=100, blank=True)
    country = models.CharField(_("Country"), max_length=100, blank=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True)
    
    # Preferences
    preferred_language = models.ForeignKey('core.Language', on_delete=models.SET_NULL, null=True, blank=True)
    notification_preferences = models.JSONField(_("Notification Preferences"), default=dict)
    
    # Verification
    is_verified = models.BooleanField(_("Verified"), default=False)
    verification_date = models.DateTimeField(_("Verification Date"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
    
    def __str__(self):
        return f"{self.user.name} - {self.get_user_type_display()} [#{self.id}]"


class ServiceProviderProfile(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Extended profile for service providers."""
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='service_provider_profile')
    
    # Business information
    business_name = models.CharField(_("Business Name"), max_length=200, blank=True)
    business_description = models.TextField(_("Business Description"), blank=True)
    business_license = models.CharField(_("Business License"), max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(_("Years of Experience"), default=0)
    
    # Service areas
    service_areas = models.JSONField(_("Service Areas"), default=list)  # List of city/area codes
    travel_radius = models.PositiveIntegerField(_("Travel Radius (km)"), default=50)
    
    # Availability
    is_available = models.BooleanField(_("Available for Work"), default=True)
    availability_schedule = models.JSONField(_("Availability Schedule"), default=dict)
    
    # Ratings and reviews
    average_rating = models.DecimalField(_("Average Rating"), max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(_("Total Reviews"), default=0)
    
    # Verification
    is_verified_provider = models.BooleanField(_("Verified Provider"), default=False)
    verification_documents = models.JSONField(_("Verification Documents"), default=list)
    
    class Meta:
        verbose_name = _("Service Provider Profile")
        verbose_name_plural = _("Service Provider Profiles")
    
    def __str__(self):
        return f"{self.user_profile.user.name} - Service Provider [#{self.id}]"


class ServiceProviderService(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Services offered by service providers."""
    provider = models.ForeignKey(ServiceProviderProfile, on_delete=models.CASCADE, related_name='services')
    subcategory = models.ForeignKey('core.ServiceSubcategory', on_delete=models.CASCADE, related_name='providers')
    
    # Service details
    description = models.TextField(_("Service Description"))
    base_price = models.DecimalField(_("Base Price"), max_digits=10, decimal_places=2)
    price_type = models.CharField(_("Price Type"), max_length=20, choices=[
        ('fixed', _('Fixed Price')),
        ('hourly', _('Hourly Rate')),
        ('negotiable', _('Negotiable')),
    ], default='fixed')
    
    # Availability
    is_available = models.BooleanField(_("Available"), default=True)
    estimated_duration = models.PositiveIntegerField(_("Estimated Duration (hours)"), null=True, blank=True)
    
    # Add-ons
    available_addons = models.ManyToManyField('core.ServiceAddon', blank=True, related_name='providers')
    
    class Meta:
        verbose_name = _("Service Provider Service")
        verbose_name_plural = _("Service Provider Services")
        unique_together = ['provider', 'subcategory']
    
    def __str__(self):
        return f"{self.provider.user_profile.user.name} - {self.subcategory.name} [#{self.id}]"


class ClientProfile(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Extended profile for clients."""
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='client_profile')
    
    # Client preferences
    preferred_service_areas = models.JSONField(_("Preferred Service Areas"), default=list)
    budget_preferences = models.JSONField(_("Budget Preferences"), default=dict)
    
    # Order history
    total_orders = models.PositiveIntegerField(_("Total Orders"), default=0)
    completed_orders = models.PositiveIntegerField(_("Completed Orders"), default=0)
    cancelled_orders = models.PositiveIntegerField(_("Cancelled Orders"), default=0)
    
    # Favorites
    favorite_providers = models.ManyToManyField(ServiceProviderProfile, blank=True, related_name='favorite_clients')
    
    class Meta:
        verbose_name = _("Client Profile")
        verbose_name_plural = _("Client Profiles")
    
    def __str__(self):
        return f"{self.user_profile.user.name} - Client [#{self.id}]"


class UserVerification(AbstractTimestampedModel):
    """User verification records."""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='verifications')
    verification_type = models.CharField(_("Verification Type"), max_length=50, choices=[
        ('phone', _('Phone Number')),
        ('email', _('Email Address')),
        ('identity', _('Identity Document')),
        ('business', _('Business License')),
        ('background_check', _('Background Check')),
    ])
    
    # Verification details
    verification_data = models.JSONField(_("Verification Data"), default=dict)
    verification_status = models.CharField(_("Status"), max_length=20, choices=[
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ], default='pending')
    
    # Admin notes
    admin_notes = models.TextField(_("Admin Notes"), blank=True)
    verified_by = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifications_approved')
    verified_at = models.DateTimeField(_("Verified At"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("User Verification")
        verbose_name_plural = _("User Verifications")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user_profile.user.name} - {self.get_verification_type_display()} [#{self.id}]"
