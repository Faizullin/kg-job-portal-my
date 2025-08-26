from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token

# PathAndRename import removed - using simple string path instead
from utils.abstract_models import AbstractSoftDeleteModel, SoftDeleteManager


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


class UserTypes:
    free = 'free'
    paid = 'paid'
    premium_paid = 'premium_paid'

    @classmethod
    def choices(cls):
        return [
            (cls.free, 'Бесплатный'),
            (cls.paid, 'Оплаченный'),
            (cls.premium_paid, 'Премиум оплаченный'),
        ]


class UserModel(AbstractUser, AbstractSoftDeleteModel):
    # Use the custom manager
    objects = UserManager()
    
    user_type = models.CharField(max_length=20, choices=UserTypes.choices(), default=UserTypes.free, )
    blocked = models.BooleanField(default=False)
    firebase_user_id = models.CharField(max_length=200, null=True, blank=True)
    fcm_token = models.CharField(max_length=255, null=True, blank=True)  # for push notifications

    # user data
    name = models.CharField(max_length=255, verbose_name='Имя')
    email = models.EmailField(max_length=255, unique=True, verbose_name='Email')
    description = models.TextField(verbose_name='Описание')
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True, verbose_name='Фото')
    photo_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на фото (Firebase)')

    # user social data
    friends = models.ManyToManyField("self", blank=True, verbose_name='Друзья', symmetrical=True)
    friendship_requests = models.ManyToManyField("self", blank=True, symmetrical=False,
                                                 related_name='pending_friend_requests',
                                                 verbose_name='Запросы в друзья')

    # App related stuff
    timezone_difference = models.IntegerField(default=0, verbose_name='Разница во времени')
    points = models.IntegerField(default=0, verbose_name='Баллы')
    day_streak = models.IntegerField(default=0, verbose_name='Дневная серия')
    max_day_streak = models.IntegerField(default=0, verbose_name='Максимальная дневная серия')

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f'{self.pk} Profile of {self.email}'

    def delete(self, using=None, keep_parents=False):
        """Override delete to implement soft delete with additional cleanup."""
        # Soft delete the user
        super().delete(using, keep_parents)
        
        # Additional cleanup for soft-deleted users
        self._cleanup_deleted_user()
    
    def _cleanup_deleted_user(self):
        """Clean up user data when soft-deleted."""
        # Clear sensitive data
        self.fcm_token = None
        self.firebase_user_id = None
        
        # Clear social connections
        self.friends.clear()
        self.friendship_requests.clear()
        
        # Save the cleanup
        self.save(update_fields=['fcm_token', 'firebase_user_id'])
    
    def restore(self, strict=True):
        """Restore a soft-deleted user."""
        super().restore(strict)
        
        # Reactivate the user account
        self.is_active = True
        self.save(update_fields=['is_active'])

    def add_points(self, points: int, description: str):
        if points < 0:
            raise ValueError('Points must be positive')
        if description == '':
            raise ValueError('Description must be filled')
        self.points += points
        self.save()
        UserPointAddHistory.objects.create(user=self, points=points, description=description)

    def is_paid(self):
        return self.user_type in (UserTypes.paid, UserTypes.premium_paid)

    def current_datetime(self) -> timezone.datetime:
        return timezone.now() + timezone.timedelta(hours=self.timezone_difference)

    def remaining_hours_till_streak_reset(self) -> int:
        last_active_date = self.activity_dates.first()
        if last_active_date is None:
            return -1

        # прибавляем разницу часов потому что ласт актив дейттайм в UTC
        last_datetime = last_active_date.datetime + timezone.timedelta(hours=self.timezone_difference)

        # разница в часах до след дня КОГДА пользователь получил +1 к страйку
        hours_till_tomorrow = 24 - last_datetime.hour

        difference = (self.current_datetime() - last_datetime).total_seconds() // 3600
        return hours_till_tomorrow + 24 - difference

    def send_friend_request(self, to_user):
        if (to_user != self) and (to_user not in self.friends.all()):
            if self.friendship_requests.filter(pk=to_user.pk).exists():
                self.accept_friend_request(to_user)
            else:
                to_user.friendship_requests.add(self)

    def accept_friend_request(self, from_user):
        if from_user in self.friendship_requests.all():
            self.friendship_requests.remove(from_user)
            self.friends.add(from_user)
            from_user.friends.add(self)

    def decline_friend_request(self, from_user):
        if from_user in self.friendship_requests.all():
            self.friendship_requests.remove(from_user)


class NotificationSettings(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='notification_settings')
    periodic_lesson_reminder = models.BooleanField(default=True)
    friend_request_notification = models.BooleanField(default=True)
    streak_notification = models.BooleanField(default=True)
    global_event_notification = models.BooleanField(default=True)

    last_streak_notification = models.DateTimeField(default=timezone.datetime(2021, 1, 1))
    last_lesson_reminder = models.DateTimeField(default=timezone.datetime(2021, 1, 1))

    class Meta:
        verbose_name = 'Настройки уведомлений'
        verbose_name_plural = 'Настройки уведомлений'

    def __str__(self):
        return f'{self.pk} Настройки уведомлении'


class UserActivityDateModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='activity_dates')
    datetime = models.DateTimeField(default=timezone.now, verbose_name='Дата активности')

    class Meta:
        verbose_name = 'Активность пользователя'
        verbose_name_plural = 'Активности пользователей'
        ordering = ['-datetime']

    def __str__(self):
        return f'{self.pk} Activity '


class UserPointAddHistory(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='point_add_history')
    points = models.IntegerField()
    description = models.TextField()
    created_date = models.DateTimeField(default=timezone.now, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'История добавления баллов'
        verbose_name_plural = 'Истории добавления баллов'

    def __str__(self):
        return f'{self.pk} UserPointAddHistory'


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
