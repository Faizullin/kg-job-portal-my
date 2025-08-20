from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.request import Request

from api_users.serializers import *
from api_users.models import *
from api_users.serializers.model_serializers import UserModelSerializer
from backend.global_function import success_with_text, error_with_text


class SetFCMToken(APIView):
    def post(self, request: Request, *args, **kwargs):
        user: UserModel = request.user
        token = request.data.get('token', None)
        if token is None:
            return error_with_text('Token is required')
        user.fcm_token = token
        user.save()
        return success_with_text(UserModelSerializer(user).data)


class GetUserView(APIView):
    def get(self, request: Request):
        user: UserModel = request.user
        user.last_login = timezone.now()
        user.save()

        # Проверка на дневную серию (если пропущено то обновляем)
        last_active_date = user.activity_dates.first()
        if last_active_date is not None:
            if user.remaining_hours_till_streak_reset() <= 0:
                user.day_streak = 0
                user.save()

        user.last_login = timezone.now()
        return success_with_text(UserModelSerializer(user).data)


class UpdateDayStreak(APIView):
    def post(self, request: Request):
        user: UserModel = request.user

        # Некая фильтрация
        # Если прошло меньше 5ти минут с последнего входа, то не обновляем активность
        # Если прошло больше 15ти с последнего входа, то просим юзера заново залогиниться
        last_login_difference = (timezone.now() - user.last_login).seconds
        if last_login_difference < 300:
            return error_with_text('Too early to update activity date')
        elif last_login_difference > 900:
            return error_with_text('Too late to update activity date, login again')

        # Логика самого day streak
        user_now_date = user.current_datetime().date()
        if UserActivityDateModel.objects.filter(datetime__date=user_now_date, user=user).exists():
            return error_with_text('Already updated today')

        user.day_streak += 1
        if user.day_streak > user.max_day_streak:
            user.max_day_streak = user.day_streak
        user.save()
        user.add_points(points=1, description='Бонус за дневную серию')

        # Если у пользователя 10 дней подряд, то даем ему 5 бонусных баллов
        if user.day_streak % 10 == 0:
            user.add_points(points=5, description='Бонусы за 10 дней подряд')

        # Создаем новую активность
        user.activity_dates.create()

        return success_with_text(UserModelSerializer(user).data)


class UpdateTimezoneDifferenceView(APIView):
    def post(self, request: Request):
        user: UserModel = request.user
        difference = request.data.get('offset', None)
        if difference is None:
            return error_with_text('Offset is required')
        difference = int(difference)
        user.timezone_difference = difference
        user.save()
        return success_with_text('Timezone difference updated')


class DeleteAccountView(APIView):
    def post(self, request: Request):
        DeletedUsersModel.objects.create(
            email=request.user.email,
            firebase_user_id=request.user.firebase_user_id,
            name=request.user.name,
            description=request.user.description
        )
        request.user.delete()
        return success_with_text('Account deleted')


class LogOutView(APIView):
    def post(self, request: Request):
        Token.objects.filter(user=request.user).delete()
        return success_with_text('Logged out')
