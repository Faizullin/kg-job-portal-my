from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from job_portal.apps.attachments.models import Attachment
from job_portal.apps.core.models import ServiceSubcategory
from job_portal.apps.locations.models import City
from job_portal.apps.resumes.models import MasterResume
from job_portal.apps.users.models import Skill, Master, Employer, Company
from utils.abstract_models import AbstractSoftDeleteModel, AbstractTimestampedModel, AbstractCascadingSoftDeleteModel, \
    TitleField, AutoSlugField, AvailableField, AdvancedLocationField

UserModel = get_user_model()


class JobUrgency(models.TextChoices):
    LOW = 'low', _('Low')
    MEDIUM = 'medium', _('Medium')
    HIGH = 'high', _('High')
    URGENT = 'urgent', _('Urgent')


class JobStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    PUBLISHED = 'published', _('Published')
    ASSIGNED = 'assigned', _('Assigned')
    IN_PROGRESS = 'in_progress', _('In Progress')
    COMPLETED = 'completed', _('Completed')
    CANCELLED = 'cancelled', _('Cancelled')


class JobType(models.TextChoices):
    FULL_TIME = 'full_time', _('Full-Time')
    PART_TIME = 'part_time', _('Part-Time')
    INTERNSHIP = 'internship', _('Internship')


class Job(AbstractCascadingSoftDeleteModel, AbstractTimestampedModel):
    """Model representing a job posted by an employer."""

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='jobs')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs', null=True, blank=True)

    title = TitleField()
    slug = AutoSlugField(populate_from="title")
    description = models.TextField(_("Description"))
    is_available = AvailableField()
    service_subcategory = models.ForeignKey(ServiceSubcategory, on_delete=models.SET_NULL, related_name='jobs',
                                            null=True)
    job_type = models.CharField(_("Job Type"), max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    special_requirements = models.TextField(_("Special Requirements"), blank=True)

    city = models.ForeignKey(City, on_delete=models.SET_NULL, related_name='jobs', null=True)
    location = AdvancedLocationField()
    skills = models.ManyToManyField(Skill, related_name='jobs', blank=True)
    attachments = models.ManyToManyField(Attachment, related_name='jobs', blank=True)

    # Service requirements
    service_date = models.DateField(_("Preferred Service Date"), null=True, blank=True)
    service_time = models.TimeField(_("Preferred Service Time"), null=True, blank=True)
    urgency = models.CharField(_("Urgency"), max_length=20, choices=JobUrgency.choices, default=JobUrgency.MEDIUM)

    # Budget and pricing
    budget_min = models.DecimalField(_("Minimum Budget"), max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(_("Maximum Budget"), max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(_("Final Price"), max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(_("Job Status"), max_length=20, choices=JobStatus.choices, default=JobStatus.DRAFT)
    published_at = models.DateTimeField(_("Published At"), null=True, blank=True)
    assigned_at = models.DateTimeField(_("Assigned At"), null=True, blank=True)
    started_at = models.DateTimeField(_("Started At"), null=True, blank=True)
    completed_at = models.DateTimeField(_("Completed At"), null=True, blank=True)
    cancelled_at = models.DateTimeField(_("Cancelled At"), null=True, blank=True)

    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")
        ordering = ['-created_at']

    def __str__(self):
        return f"Job: {self.title} [#{self.id}]"


class JobApplicationStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    ACCEPTED = 'accepted', _('Accepted')
    REJECTED = 'rejected', _('Rejected')
    WITHDRAWN = 'withdrawn', _('Withdrawn')


class JobApplication(AbstractSoftDeleteModel, AbstractTimestampedModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='applications',
                                  null=True, blank=True)

    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    comment = models.TextField(_("Comment"), blank=True)
    estimated_duration = models.PositiveIntegerField(_("Estimated Duration (hours)"), null=True, blank=True)
    resume = models.ForeignKey(MasterResume, on_delete=models.SET_NULL, related_name='job_applications', blank=True,
                               null=True)

    status = models.CharField(_("Status"), max_length=20, choices=JobApplicationStatus.choices,
                              default=JobApplicationStatus.PENDING)

    applied_at = models.DateTimeField(_("Applied On"), auto_now_add=True)
    accepted_at = models.DateTimeField(_("Accepted At"), null=True, blank=True)
    rejected_at = models.DateTimeField(_("Rejected At"), null=True, blank=True)
    withdrawn_at = models.DateTimeField(_("Withdrawn At"), null=True, blank=True)

    class Meta:
        verbose_name = _("Job Application")
        verbose_name_plural = _("Job Applications")
        ordering = ['amount', '-created_at']
        unique_together = ['job', 'applicant']

    def __str__(self):
        return f"{self.applicant.user.username} - {self.job.title} [#{self.id}]"


class JobAssignmentStatus(models.TextChoices):
    ASSIGNED = 'assigned', _('Assigned')
    IN_PROGRESS = 'in_progress', _('In Progress')
    COMPLETED = 'completed', _('Completed')
    CANCELLED = 'cancelled', _('Cancelled')


class JobAssignment(AbstractTimestampedModel):
    """Model representing the assignment of a job to a master."""

    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='assignment')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='assignments')
    accepted_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='assignment')
    status = models.CharField(_("Assignment Status"), max_length=20, choices=JobAssignmentStatus.choices,
                              default=JobAssignmentStatus.ASSIGNED)

    # Assignment details
    assigned_at = models.DateTimeField(_("Assigned At"), auto_now_add=True)
    started_at = models.DateTimeField(_("Started At"), null=True, blank=True)
    completed_at = models.DateTimeField(_("Completed At"), null=True, blank=True)

    # Progress tracking
    progress_notes = models.TextField(_("Progress Notes"), blank=True)
    completion_notes = models.TextField(_("Completion Notes"), blank=True)
    attachments = models.ManyToManyField(Attachment, blank=True, related_name='assignments', )

    # Client feedback
    client_rating = models.PositiveIntegerField(_("Client Rating"), null=True, blank=True,
                                                validators=[MinValueValidator(1), MaxValueValidator(5)])
    client_review = models.TextField(_("Client Review"), blank=True)

    class Meta:
        verbose_name = _("Job Assignment")
        verbose_name_plural = _("Job Assignments")

    def __str__(self):
        return f"{self.job.title} - {self.master.user.username} [#{self.id}]"


class JobDisputeType(models.TextChoices):
    PAYMENT_ISSUE = 'payment_issue', _('Payment Issue')
    SERVICE_QUALITY = 'service_quality', _('Service Quality')
    TIMELINESS = 'timeliness', _('Timeliness')
    OTHER = 'other', _('Other')


class DisputeStatus(models.TextChoices):
    OPEN = 'open', _('Open')
    UNDER_REVIEW = 'under_review', _('Under Review')
    RESOLVED = 'resolved', _('Resolved')
    CLOSED = 'closed', _('Closed')


class JobDispute(AbstractTimestampedModel):
    """Model representing disputes raised on jobs."""

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='disputes')
    raised_by = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='disputes_raised')

    # Dispute details
    dispute_type = models.CharField(_("Dispute Type"), max_length=50, choices=JobDisputeType.choices,
                                    default=JobDisputeType.OTHER)
    description = models.TextField(_("Description"))
    evidence = models.JSONField(_("Evidence"), default=list)  # List of file URLs

    # Resolution
    status = models.CharField(_("Status"), max_length=20, choices=DisputeStatus.choices, default=DisputeStatus.OPEN)

    # Admin handling
    admin_notes = models.TextField(_("Admin Notes"), blank=True)
    resolved_by = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='disputes_resolved')
    resolved_at = models.DateTimeField(_("Resolved At"), null=True, blank=True)
    resolution = models.TextField(_("Resolution"), blank=True)

    class Meta:
        verbose_name = _("Job Dispute")
        verbose_name_plural = _("Job Disputes")
        ordering = ['-created_at']

    def __str__(self):
        return f"Dispute on {self.job.title} - {self.get_dispute_type_display()} [#{self.id}]"


class BookmarkJob(AbstractTimestampedModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} bookmarked {self.job.title} [#{self.id}]"


class FavoriteJob(AbstractTimestampedModel):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} favorited {self.job.title} [#{self.id}]"
