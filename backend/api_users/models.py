from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from protected_media.models import ProtectedImageField
from rest_framework.authtoken.models import Token

from backend.global_function import PathAndRename


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


class UserModel(AbstractUser):
    user_type = models.CharField(max_length=20, choices=UserTypes.choices(), default=UserTypes.free, )
    blocked = models.BooleanField(default=False)
    firebase_user_id = models.CharField(max_length=200, null=True, blank=True)
    fcm_token = models.CharField(max_length=255, null=True, blank=True)  # for push notifications

    # user data
    name = models.CharField(max_length=255, verbose_name='Имя')
    email = models.EmailField(max_length=255, unique=True, verbose_name='Email')
    description = models.TextField(verbose_name='Описание')
    photo = ProtectedImageField(upload_to=PathAndRename('user_photos/'), blank=True, null=True, verbose_name='Фото')
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


class DeletedUsersModel(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    email = models.EmailField(max_length=255, unique=True)
    firebase_user_id = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=255, verbose_name='Имя')
    description = models.TextField(verbose_name='Описание')


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
