from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import UserModel
from job_portal.apps.core.models import ServiceCategory, ServiceArea, ServiceSubcategory
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel


class Gender(models.TextChoices):
    MALE = 'male', _('Male')
    FEMALE = 'female', _('Female')
    OTHER = 'other', _('Other')
    PREFER_NOT_TO_SAY = 'prefer_not_to_say', _('Prefer not to say')


class UserProfile(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Extended user profile for job portal functionality."""

    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='job_portal_profile')

    # Profile information
    bio = models.TextField(_("Bio"), blank=True)
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)
    gender = models.CharField(_("Gender"), max_length=20, choices=Gender.choices, blank=True)

    # Contact information
    phone_number = models.CharField(_("Phone Number"), max_length=20, blank=True)
    address = models.TextField(_("Address"), blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    state = models.CharField(_("State/Province"), max_length=100, blank=True)
    country = models.CharField(_("Country"), max_length=100, blank=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True)

    # Terms and conditions
    terms_accepted = models.BooleanField(_("Terms Accepted"), default=False)
    terms_accepted_at = models.DateTimeField(_("Terms Accepted At"), null=True, blank=True)

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
        return f"{self.user.username} - Profile [#{self.id}]"


class ServiceProviderProfile(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Extended profile for service providers."""
    # Uses default SoftDeleteManager from AbstractSoftDeleteModel

    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='service_provider_profile')

    # Business information
    business_name = models.CharField(_("Business Name"), max_length=200, blank=True)
    business_description = models.TextField(_("Business Description"), blank=True)
    profession = models.ForeignKey('Profession', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='providers')

    # Locations and services
    service_areas = models.ManyToManyField(ServiceArea, blank=True, related_name='providers')
    services_offered = models.ManyToManyField(ServiceSubcategory, blank=True, related_name='providers_offering_service')

    # Work modes
    works_remotely = models.BooleanField(_("Works Remotely"), default=False)
    accepts_clients_at_location = models.BooleanField(_("Accepts Clients at Location"), default=False)
    travels_to_clients = models.BooleanField(_("Travels to Clients"), default=True)

    # Availability and pricing
    is_available = models.BooleanField(_("Available for Work"), default=True)
    hourly_rate = models.DecimalField(_("Hourly Rate"), max_digits=10, decimal_places=2, null=True, blank=True)
    response_time_hours = models.PositiveIntegerField(_("Response Time (hours)"), default=24)

    # Professional information
    work_experience_start_year = models.PositiveIntegerField(_("Work Experience Start Year"), null=True, blank=True)
    education_institution = models.CharField(_("Education Institution"), max_length=200, blank=True)
    education_years = models.CharField(_("Education Years"), max_length=20, blank=True, help_text=_("e.g., 2005-2009"))
    languages = models.JSONField(_("Languages"), default=list, help_text=_("List of languages spoken"))
    about_description = models.TextField(_("About Description"), blank=True)

    # Location and availability
    current_location = models.CharField(_("Current Location"), max_length=200, blank=True)
    is_online = models.BooleanField(_("Is Online"), default=False)
    last_seen = models.DateTimeField(_("Last Seen"), null=True, blank=True)

    # Status flags
    is_verified_provider = models.BooleanField(_("Verified Provider"), default=False)
    is_top_master = models.BooleanField(_("Top Master"), default=False)

    class Meta:
        verbose_name = _("Service Provider Profile")
        verbose_name_plural = _("Service Provider Profiles")

    def __str__(self):
        return f"{self.user_profile.user.username} - Service Provider [#{self.id}]"


class ClientProfile(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Extended profile for clients."""
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='client_profile')

    # Client preferences
    preferred_services = models.ManyToManyField(ServiceSubcategory, blank=True,
                                                related_name='client_preferences')

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
        return f"{self.user_profile.user.username} - Client [#{self.id}]"


class MasterSkill(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Skills that service providers can have."""
    name = models.CharField(_("Skill Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='skills')
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Master Skill")
        verbose_name_plural = _("Master Skills")
        ordering = ['name']

    def __str__(self):
        return f"{self.name}... [#{self.id}]"


class ProficiencyLevel(models.TextChoices):
    BEGINNER = 'beginner', _('Beginner')
    INTERMEDIATE = 'intermediate', _('Intermediate')
    ADVANCED = 'advanced', _('Advanced')
    EXPERT = 'expert', _('Expert')


class ServiceProviderSkill(AbstractTimestampedModel):
    """Many-to-many relationship between service providers and skills."""
    service_provider = models.ForeignKey(ServiceProviderProfile, on_delete=models.CASCADE,
                                         related_name='provider_skills')
    skill = models.ForeignKey(MasterSkill, on_delete=models.CASCADE, related_name='providers')
    proficiency_level = models.CharField(_("Proficiency Level"), max_length=20, choices=ProficiencyLevel.choices,
                                         default=ProficiencyLevel.INTERMEDIATE)
    years_of_experience = models.PositiveIntegerField(_("Years of Experience"), default=0)
    is_primary_skill = models.BooleanField(_("Primary Skill"), default=False)

    class Meta:
        verbose_name = _("Service Provider Skill")
        verbose_name_plural = _("Service Provider Skills")
        unique_together = ['service_provider', 'skill']

    def __str__(self):
        return f"{self.service_provider.user_profile.user.username} - {self.skill.name} [#{self.id}]"


class PortfolioItem(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Portfolio examples of service provider's work."""
    service_provider = models.ForeignKey(ServiceProviderProfile, on_delete=models.CASCADE,
                                         related_name='portfolio_items')
    title = models.CharField(_("Work Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    image = models.ImageField(_("Portfolio Image"), upload_to='portfolio_images/')
    skill_used = models.ForeignKey(MasterSkill, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='portfolio_items')
    is_featured = models.BooleanField(_("Featured Example"), default=False)

    class Meta:
        verbose_name = _("Portfolio Item")
        verbose_name_plural = _("Portfolio Items")
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.service_provider.user_profile.user.username} - {self.title}... [#{self.id}]"


class Certificate(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Professional certificates and qualifications."""
    service_provider = models.ForeignKey(ServiceProviderProfile, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(_("Certificate Name"), max_length=200)
    issuing_organization = models.CharField(_("Issuing Organization"), max_length=200)
    certificate_number = models.CharField(_("Certificate Number"), max_length=100, blank=True)
    issue_date = models.DateField(_("Issue Date"), null=True, blank=True)
    expiry_date = models.DateField(_("Expiry Date"), null=True, blank=True)
    certificate_file = models.FileField(_("Certificate File"), upload_to='certificates/', blank=True)
    is_verified = models.BooleanField(_("Verified"), default=False)

    class Meta:
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.service_provider.user_profile.user.username} - {self.name}... [#{self.id}]"


class Profession(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Available professions for service providers."""
    name = models.CharField(_("Profession Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='professions')
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Profession")
        verbose_name_plural = _("Professions")
        ordering = ['name']

    def __str__(self):
        return f"{self.name}... [#{self.id}]"


class ProviderStatistics(AbstractTimestampedModel):
    """Statistics for service providers."""
    provider = models.OneToOneField(ServiceProviderProfile, on_delete=models.CASCADE, related_name='statistics')

    # Performance metrics
    total_jobs_completed = models.PositiveIntegerField(_("Total Jobs Completed"), default=0)
    on_time_percentage = models.DecimalField(_("On Time Percentage"), max_digits=5, decimal_places=2, default=0.00)
    repeat_customer_percentage = models.DecimalField(_("Repeat Customer Percentage"), max_digits=5, decimal_places=2,
                                                     default=0.00)

    # Ratings and reviews
    average_rating = models.DecimalField(_("Average Rating"), max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(_("Total Reviews"), default=0)

    class Meta:
        verbose_name = _("Provider Statistics")
        verbose_name_plural = _("Provider Statistics")

    def __str__(self):
        return f"{self.provider.user_profile.user.username} Statistics... [#{self.id}]"
