from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from job_portal.apps.core.models import ServiceCategory, ServiceArea, ServiceSubcategory
from job_portal.apps.attachments.models import Attachment
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel, TitleField, ActiveField, \
    PhoneNumberField

UserModel = get_user_model()


class Gender(models.TextChoices):
    MALE = 'male', _('Male')
    FEMALE = 'female', _('Female')


class Profession(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Available professions for masters"""

    name = TitleField(unique=True)
    description = models.TextField(_("Description"), blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='professions')
    is_active = ActiveField()

    class Meta:
        verbose_name = _("Profession")
        verbose_name_plural = _("Professions")
        ordering = ['name']

    def __str__(self):
        return f"{self.name}... [#{self.id}]"


class Master(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Extended profile for masters."""

    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='master_profile')

    # Business information
    profession = models.ForeignKey(Profession, on_delete=models.SET_NULL, null=True, blank=True, related_name="masters")

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

    skills = models.ManyToManyField('Skill', through='MasterSkill', related_name='masters')

    class Meta:
        verbose_name = _("Master Profile")
        verbose_name_plural = _("Master Profiles")

    def __str__(self):
        return f"{self.user.username} - Master [#{self.id}]"


class Employer(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Extended profile for employers."""

    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='employer_profile')
    
    # Contact information
    contact_phone = PhoneNumberField(blank=True)

    preferred_services = models.ManyToManyField(ServiceSubcategory, blank=True,
                                                related_name='employer_preferences')

    total_orders = models.PositiveIntegerField(_("Total Orders"), default=0)
    completed_orders = models.PositiveIntegerField(_("Completed Orders"), default=0)
    cancelled_orders = models.PositiveIntegerField(_("Cancelled Orders"), default=0)

    # Favorites
    favorite_masters = models.ManyToManyField(Master, blank=True, related_name='favorite_employers')

    class Meta:
        verbose_name = _("Employer Profile")
        verbose_name_plural = _("Employer Profiles")

    def __str__(self):
        return f"{self.user.username} - Employer [#{self.id}]"


class Skill(AbstractSoftDeleteModel, AbstractTimestampedModel):
    name = TitleField()
    description = models.TextField(_("Description"), blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='skills')
    is_active = ActiveField()

    class Meta:
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")
        ordering = ['name']

    def __str__(self):
        return f"{self.name}... [#{self.id}]"


class MasterSkillProficiencyLevel(models.TextChoices):
    BEGINNER = 'beginner', _('Beginner')
    INTERMEDIATE = 'intermediate', _('Intermediate')
    ADVANCED = 'advanced', _('Advanced')
    EXPERT = 'expert', _('Expert')


class MasterSkill(AbstractTimestampedModel):
    """Skills associated with a master."""

    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='master_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='providers')
    proficiency_level = models.CharField(_("Proficiency Level"), max_length=20,
                                         choices=MasterSkillProficiencyLevel.choices,
                                         default=MasterSkillProficiencyLevel.INTERMEDIATE)
    years_of_experience = models.PositiveIntegerField(_("Years of Experience"), default=0)
    is_primary_skill = models.BooleanField(_("Primary Skill"), default=False)

    class Meta:
        verbose_name = _("Master Skill")
        verbose_name_plural = _("Master Skills")
        unique_together = ['master', 'skill']

    def __str__(self):
        return f"{self.master.user.username} - {self.skill.name} [#{self.id}]"




class PortfolioItem(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Portfolio items showcasing a master's work."""

    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='portfolio_items')
    title = TitleField()
    description = models.TextField(_("Description"), blank=True)
    attachments = models.ManyToManyField(Attachment, related_name='portfolio_items', blank=True)
    skill_used = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='portfolio_items')
    is_featured = models.BooleanField(_("Featured Item"), default=False)

    class Meta:
        verbose_name = _("Portfolio Item")
        verbose_name_plural = _("Portfolio Items")
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.master.user.username} - {self.title}... [#{self.id}]"


def certificate_storage_upload_to(instance, filename):
    """Generate upload path for attachments."""

    current_datetime = timezone.now().strftime('%Y/%m/%d')
    if not instance.pk:
        raise ValueError("Instance must have a primary key before uploading.")
    updated_filename = f"{current_datetime}_{filename}"
    return f'certificates/attachment_{instance.pk}/{updated_filename}'


class Certificate(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Certificates and qualifications of a master."""

    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='certificates')
    name = TitleField()
    issuing_organization = models.CharField(_("Issuing Organization"), max_length=200)
    certificate_number = models.CharField(_("Certificate Number"), max_length=100, blank=True)
    issue_date = models.DateField(_("Issue Date"), null=True, blank=True)
    expiry_date = models.DateField(_("Expiry Date"), null=True, blank=True)
    certificate_file = models.FileField(_("Certificate File"), upload_to=certificate_storage_upload_to, blank=True, null=True)
    is_verified = models.BooleanField(_("Verified"), default=False)

    class Meta:
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.master.user.username} - {self.name}... [#{self.id}]"


class MasterStatistics(AbstractTimestampedModel):
    """Statistical data related to masters."""

    master = models.OneToOneField(Master, on_delete=models.CASCADE, related_name='statistics')

    # Performance metrics
    total_jobs_completed = models.PositiveIntegerField(_("Total Jobs Completed"), default=0)
    on_time_percentage = models.DecimalField(_("On Time Percentage"), max_digits=5, decimal_places=2, default=0.00)
    repeat_customer_percentage = models.DecimalField(_("Repeat Customer Percentage"), max_digits=5, decimal_places=2,
                                                     default=0.00)

    # Ratings and reviews
    average_rating = models.DecimalField(_("Average Rating"), max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(_("Total Reviews"), default=0)

    class Meta:
        verbose_name = _("Master Statistics")
        verbose_name_plural = _("Master Statistics")

    def __str__(self):
        return f"{self.master.user.username} Statistics... [#{self.id}]"


class Company(AbstractTimestampedModel):
    """Companies that masters can be associated with."""

    name = TitleField()
    description = models.TextField(_("Description"), blank=True)
    website = models.URLField(_("Website"), blank=True)
    contact_email = models.EmailField(_("Contact Email"), blank=True)
    contact_phone = PhoneNumberField(blank=True)
    address = models.CharField(_("Address"), max_length=255, blank=True)
    is_active = ActiveField()

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        ordering = ['name']

    def __str__(self):
        return f"{self.name}... [#{self.id}]"
