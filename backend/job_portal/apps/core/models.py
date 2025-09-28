from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel, TitleField, AutoSlugField, \
    ActiveField


class ComplexityLevel(models.TextChoices):
    BEGINNER = 'beginner', _('Beginner')
    INTERMEDIATE = 'intermediate', _('Intermediate')
    ADVANCED = 'advanced', _('Advanced')
    EXPERT = 'expert', _('Expert')


class PriceType(models.TextChoices):
    FIXED = 'fixed', _('Fixed Price')
    PERCENTAGE = 'percentage', _('Percentage of Base Price')
    PER_UNIT = 'per_unit', _('Per Unit')
    PER_HOUR = 'per_hour', _('Per Hour')


class SettingType(models.TextChoices):
    STRING = 'string', _('String')
    INTEGER = 'integer', _('Integer')
    BOOLEAN = 'boolean', _('Boolean')
    JSON = 'json', _('JSON')
    FILE = 'file', _('File')


class Platform(models.TextChoices):
    ANDROID = 'android', _('Android')
    IOS = 'ios', _('iOS')
    WEB = 'web', _('Web')
    ALL = 'all', _('All Platforms')


class FAQCategory(models.TextChoices):
    GENERAL = 'general', _('General')
    SPECIALIST = 'specialist', _('Specialist')
    REVIEWS = 'reviews', _('Reviews')
    ACCOUNT = 'account', _('Account')
    SEARCH = 'search', _('Search')
    SAFETY = 'safety', _('Safety')


class Language(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Supported languages for the application."""

    name = TitleField(max_length=50)
    code = models.CharField(_("Language Code"), max_length=5, unique=True)
    native_name = models.CharField(_("Native Name"), max_length=50)
    is_active = ActiveField()
    is_default = models.BooleanField(_("Default Language"), default=False)

    # Additional features
    flag_icon = models.CharField(_("Flag Icon"), max_length=50, blank=True)
    rtl_support = models.BooleanField(_("RTL Support"), default=False)
    locale_code = models.CharField(_("Locale Code"), max_length=10, blank=True)
    currency_code = models.CharField(_("Currency Code"), max_length=3, blank=True)

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})... [#{self.id}]"


class ServiceCategory(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Main service categories (e.g., Cleaning, Plumbing, etc.)."""

    name = TitleField()
    slug = AutoSlugField(populate_from="name")
    description = models.TextField(_("Description"))
    icon = models.CharField(_("Icon"), max_length=50, blank=True)
    color = models.CharField(_("Color"), max_length=7, default="#6366f1")  # Hex color
    is_active = models.BooleanField(_("Active"), default=True)
    sort_order = models.PositiveIntegerField(_("Sort Order"), default=0)

    # Additional features
    banner_image = models.URLField(_("Banner Image"), blank=True)
    featured = models.BooleanField(_("Featured Category"), default=False)
    commission_rate = models.DecimalField(_("Commission Rate (%)"), max_digits=5, decimal_places=2, default=0)
    min_price = models.DecimalField(_("Minimum Price"), max_digits=10, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(_("Maximum Price"), max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_duration_min = models.PositiveIntegerField(_("Min Duration (hours)"), null=True, blank=True)
    estimated_duration_max = models.PositiveIntegerField(_("Max Duration (hours)"), null=True, blank=True)

    # SEO and marketing
    meta_title = models.CharField(_("Meta Title"), max_length=60, blank=True)
    meta_description = models.TextField(_("Meta Description"), blank=True)
    keywords = models.TextField(_("Keywords"), blank=True)

    # Requirements
    requires_license = models.BooleanField(_("Requires License"), default=False)
    requires_insurance = models.BooleanField(_("Requires Insurance"), default=False)
    requires_background_check = models.BooleanField(_("Requires Background Check"), default=False)

    class Meta:
        verbose_name = _("Service Category")
        verbose_name_plural = _("Service Categories")
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name}... [#{self.id}]"


class ServiceSubcategory(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Specific services within job types."""

    name = TitleField()
    slug = AutoSlugField(populate_from="name")
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(_("Description"))
    icon = models.CharField(_("Icon"), max_length=50, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    sort_order = models.PositiveIntegerField(_("Sort Order"), default=0)

    # Additional features
    image = models.URLField(_("Image"), blank=True)
    featured = models.BooleanField(_("Featured Subcategory"), default=False)
    base_price = models.DecimalField(_("Base Price"), max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_min = models.DecimalField(_("Price Range Min"), max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_max = models.DecimalField(_("Price Range Max"), max_digits=10, decimal_places=2, null=True, blank=True)

    # Service details
    estimated_duration = models.PositiveIntegerField(_("Estimated Duration (hours)"), null=True, blank=True)
    complexity_level = models.CharField(_("Complexity Level"), max_length=20, choices=ComplexityLevel.choices,
                                        default=ComplexityLevel.INTERMEDIATE)

    # Requirements
    safety_requirements = models.TextField(_("Safety Requirements"), blank=True)

    # SEO
    meta_title = models.CharField(_("Meta Title"), max_length=60, blank=True)
    meta_description = models.TextField(_("Meta Description"), blank=True)

    class Meta:
        verbose_name = _("Service Subcategory")
        verbose_name_plural = _("Service Subcategories")
        ordering = ['sort_order', 'name']
        unique_together = ['category', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}... [#{self.id}]"


class ServiceArea(AbstractSoftDeleteModel, AbstractTimestampedModel):
    """Geographic service areas."""
    name = models.CharField(_("Area Name"), max_length=100)
    city = models.CharField(_("City"), max_length=100)
    state = models.CharField(_("State/Province"), max_length=100)
    country = models.CharField(_("Country"), max_length=100)

    # Geographic data
    latitude = models.DecimalField(_("Latitude"), max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(_("Longitude"), max_digits=9, decimal_places=6, null=True, blank=True)
    postal_codes = models.JSONField(_("Postal Codes"), default=list)

    # Service availability
    is_active = models.BooleanField(_("Active"), default=True)
    service_categories = models.ManyToManyField(ServiceCategory, related_name='service_areas')

    # Pricing
    base_price_multiplier = models.DecimalField(_("Base Price Multiplier"), max_digits=4, decimal_places=2,
                                                default=1.00)
    travel_fee = models.DecimalField(_("Travel Fee"), max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Service Area")
        verbose_name_plural = _("Service Areas")
        ordering = ['country', 'state', 'city', 'name']
        unique_together = ['name', 'city', 'state', 'country']

    def __str__(self):
        return f"{self.city}, {self.state} - {self.name}... [#{self.id}]"


class SystemSettings(AbstractTimestampedModel):
    """System-wide configuration settings."""
    key = models.CharField(_("Setting Key"), max_length=100, unique=True)
    value = models.TextField(_("Setting Value"))
    description = models.TextField(_("Description"), blank=True)
    is_public = models.BooleanField(_("Public Setting"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)

    # Additional features
    setting_type = models.CharField(_("Setting Type"), max_length=20, choices=SettingType.choices,
                                    default=SettingType.STRING)

    # Validation
    validation_regex = models.CharField(_("Validation Regex"), max_length=200, blank=True)
    min_value = models.CharField(_("Minimum Value"), max_length=50, blank=True)
    max_value = models.CharField(_("Maximum Value"), max_length=50, blank=True)

    # Access control
    requires_admin = models.BooleanField(_("Requires Admin"), default=False)
    category = models.CharField(_("Category"), max_length=50, default='general')

    class Meta:
        verbose_name = _("System Setting")
        verbose_name_plural = _("System Settings")
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.key}... [#{self.id}]"


class AppVersion(AbstractTimestampedModel):
    """App version tracking for updates."""
    version = models.CharField(_("Version"), max_length=20, unique=True)
    build_number = models.PositiveIntegerField(_("Build Number"), unique=True)
    release_notes = models.TextField(_("Release Notes"), blank=True)
    is_forced_update = models.BooleanField(_("Forced Update"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    release_date = models.DateTimeField(_("Release Date"), auto_now_add=True)

    # Additional features
    platform = models.CharField(_("Platform"), max_length=20, choices=Platform.choices, default=Platform.ALL)

    # Update details
    download_url = models.URLField(_("Download URL"), blank=True)
    file_size = models.PositiveIntegerField(_("File Size (bytes)"), null=True, blank=True)
    checksum = models.CharField(_("Checksum"), max_length=64, blank=True)

    # Compatibility
    min_os_version = models.CharField(_("Minimum OS Version"), max_length=20, blank=True)
    max_os_version = models.CharField(_("Maximum OS Version"), max_length=20, blank=True)
    device_requirements = models.JSONField(_("Device Requirements"), default=dict)

    class Meta:
        verbose_name = _("App Version")
        verbose_name_plural = _("App Versions")
        ordering = ['-build_number']

    def __str__(self):
        return f"v{self.version} (Build {self.build_number})... [#{self.id}]"


class SupportFAQ(AbstractTimestampedModel):
    """Support FAQ items (from screen 5)."""

    question = models.CharField(_("Question"), max_length=500)
    answer = models.TextField(_("Answer"))

    # Categorization
    category = models.CharField(_("Category"), max_length=50, choices=FAQCategory.choices, default=FAQCategory.GENERAL)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='faq_items', null=True, blank=True)

    # Ordering and visibility
    sort_order = models.PositiveIntegerField(_("Sort Order"), default=0)
    is_popular = models.BooleanField(_("Popular Question"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)

    # Usage tracking
    view_count = models.PositiveIntegerField(_("View Count"), default=0)

    class Meta:
        verbose_name = _("Support FAQ")
        verbose_name_plural = _("Support FAQ")
        ordering = ['sort_order', 'question']

    def __str__(self):
        return f"{self.question[:50]}... [#{self.id}]"
