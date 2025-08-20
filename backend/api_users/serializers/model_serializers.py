from rest_framework import serializers

from api_users.models import *
from api_lessons.models import Lesson, UserLessonModel
from backend.global_function import UserContextNeededSerializer


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        exclude = ['id', 'user']


class UserModelSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    paid = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    ranking = serializers.SerializerMethodField()
    notification_settings = NotificationSettingsSerializer()

    class Meta:
        model = UserModel
        # excluding default django user fields
        fields = ['id', 'photo', 'paid', 'progress', 'ranking', 'name', 'email', 'description', 'day_streak',
                  'max_day_streak', 'fcm_token', 'notification_settings', 'timezone_difference']

    def get_photo(self, obj: UserModel):
        if obj.photo:
            return obj.photo.url
        return obj.photo_url

    def get_paid(self, obj: UserModel):
        return not (obj.user_type == UserTypes.free)

    def get_progress(self, obj: UserModel):
        all_lessons = Lesson.objects.all().count()
        user_lessons = UserLessonModel.objects.filter(user=obj, completed=True).count()
        if all_lessons == 0:
            return 1.0
        return user_lessons / all_lessons

    def get_ranking(self, obj: UserModel):
        return UserModel.objects.filter(points__gt=obj.points).count() + 1


class UserModelAsFriendSerializer(UserContextNeededSerializer, serializers.ModelSerializer):
    is_request_pending = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    ranking = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = ['id', 'name', 'photo', 'description', 'max_day_streak', 'is_request_pending', 'ranking']

    def get_photo(self, obj: UserModel):
        if obj.photo:
            return obj.photo.url
        return obj.photo_url

    def get_is_request_pending(self, obj: UserModel):
        return obj.friendship_requests.filter(id=self.user.id).exists()

    def get_ranking(self, obj: UserModel):
        return UserModel.objects.filter(points__gt=obj.points).count() + 1
