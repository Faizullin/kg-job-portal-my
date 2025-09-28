from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils.abstract_models import AbstractSoftDeleteModel, SoftDeleteManager, AbstractTimestampedModel


class UserManager(SoftDeleteManager, BaseUserManager):
    """
    Custom user manager that extends SoftDeleteManager and BaseUserManager.
    Provides soft delete functionality while maintaining Django's user creation methods.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with soft delete support."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with soft delete support."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        """Get user by natural key (username) excluding deleted users."""
        return self.get(username=username)

    def filter_by_user_type(self, user_type):
        """Filter users by user type, excluding deleted users."""
        return self.filter(user_type=user_type)

    def get_blocked_users(self):
        """Get blocked users, excluding deleted users."""
        return self.filter(blocked=True)

    def get_active_users(self):
        """Get active users (not blocked, not deleted)."""
        return self.filter(blocked=False)


class UserTypes(models.TextChoices):
    FREE = 'free', _('Бесплатный')
    PAID = 'paid', _('Оплаченный')
    PREMIUM_PAID = 'premium_paid', _('Премиум оплаченный')


def user_photo_storage_upload_to(instance, filename):
    """Generate upload path for user photos."""

    current_datetime = timezone.now().strftime('%Y/%m/%d')
    # mege updated file name
    if not instance.pk:
        raise ValueError("Instance must have a primary key before uploading a photo.")
    updated_filename = f"{current_datetime}_{filename}"
    return f'user_photos/user_{instance.pk}/{updated_filename}'


class UserModel(AbstractUser, AbstractSoftDeleteModel):
    # Use the custom manager
    objects = UserManager()

    user_type = models.CharField(max_length=20, choices=UserTypes.choices, default=UserTypes.FREE)
    blocked = models.BooleanField(default=False)
    firebase_user_id = models.CharField(max_length=200, null=True, blank=True)

    # user data
    email = models.EmailField(max_length=255, unique=True, verbose_name=_('Email'))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    photo = models.ImageField(upload_to=user_photo_storage_upload_to, blank=True, null=True, verbose_name=_("Photo"))
    photo_url = models.URLField(blank=True, null=True, verbose_name=_("Photo URL"))
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f'{self.pk} Profile of {self.email} [#{self.id}]'

    def delete(self, using=None, keep_parents=False):
        """Override delete to implement soft delete with additional cleanup."""

        super().delete(using, keep_parents)
        self._cleanup_deleted_user()

    def _cleanup_deleted_user(self):
        """Clean up user data when soft-deleted."""

        self.firebase_user_id = None
        self.save(update_fields=['firebase_user_id'])

    def restore(self, strict=True):
        """Restore a soft-deleted user."""
        super().restore(strict)

        self.is_active = True
        self.save(update_fields=['is_active'])

    def is_paid(self):
        return self.user_type in (UserTypes.PAID, UserTypes.PREMIUM_PAID)


class UserActivityDateModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='activity_dates')
    datetime = models.DateTimeField(default=timezone.now, verbose_name='Дата активности')

    class Meta:
        verbose_name = 'Активность пользователя'
        verbose_name_plural = 'Активности пользователей'
        ordering = ['-datetime']

    def __str__(self):
        return f'{self.pk} Activity '


class LoginSession(models.Model):
    """Track user login sessions for security - enhanced feature not in api_users"""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='login_sessions', verbose_name='User')
    session_key = models.CharField(max_length=40, unique=True, verbose_name='Session Key')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Address')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    login_at = models.DateTimeField(auto_now_add=True, verbose_name='Login At')
    logout_at = models.DateTimeField(null=True, blank=True, verbose_name='Logout At')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    class Meta:
        verbose_name = 'Login Session'
        verbose_name_plural = 'Login Sessions'
        ordering = ['-login_at']

    def __str__(self):
        return f"{self.user.username} - {self.login_at}"


class UserNotificationSettings(AbstractTimestampedModel):
    """User notification preferences and settings."""
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='notification_settings')

    # SMS Notifications
    sms_notifications = models.BooleanField(_("SMS Notifications"), default=True)

    # Push Notifications
    push_notifications = models.BooleanField(_("Push Notifications"), default=True)

    # Email Notifications
    email_notifications = models.BooleanField(_("Email Notifications"), default=True)

    # Task-related notifications
    task_notifications = models.BooleanField(_("Task Notifications"), default=True)
    specialist_messages = models.BooleanField(_("Specialist Messages"), default=True)
    task_updates = models.BooleanField(_("Task Updates"), default=True)

    # Marketing notifications
    marketing_emails = models.BooleanField(_("Marketing Emails"), default=False)
    promotional_sms = models.BooleanField(_("Promotional SMS"), default=False)
    newsletter = models.BooleanField(_("Newsletter"), default=False)

    # System notifications
    system_alerts = models.BooleanField(_("System Alerts"), default=True)
    security_notifications = models.BooleanField(_("Security Notifications"), default=True)

    # Quiet hours
    quiet_hours_enabled = models.BooleanField(_("Quiet Hours Enabled"), default=False)
    quiet_hours_start = models.TimeField(_("Quiet Hours Start"), null=True, blank=True)
    quiet_hours_end = models.TimeField(_("Quiet Hours End"), null=True, blank=True)

    class Meta:
        verbose_name = _("User Notification Settings")
        verbose_name_plural = _("User Notification Settings")

    def __str__(self):
        return f"{self.user.username} - Notification Settings [#{self.id}]"
