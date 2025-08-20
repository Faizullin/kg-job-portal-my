import logging
import concurrent.futures

from django.utils import timezone

from api_users.models import UserModel, NotificationSettings
from firebase_admin import messaging


def send_notification_to_user(user: UserModel, title, body, payload):
    if user.fcm_token == '':
        # get logger and warning that user has no cloud_messaging_token
        print(f'User {user} has no cloud_messaging_token')
        logging.warning(f'User {user} has no cloud_messaging_token')
        return

    print('-' * 100)
    print('User Id', user.id)
    print('title:', title)
    print('body:', body)
    print('payload:', payload)
    print('-' * 100)

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=payload,
        token=user.fcm_token,
    )

    # sending in async mode as we do not want to wait for response
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(messaging.send, message)


def send_streak_notification(user: UserModel, minutes_remaining: int):
    notification_settings: NotificationSettings = user.notification_settings
    if not notification_settings.streak_notification:
        return

    title = 'Напоминание о дневной серии!'
    body = ''
    last_streak_notification_diff = (timezone.now() - notification_settings.last_streak_notification)
    last_streak_notification_diff = last_streak_notification_diff.total_seconds() // 60
    if minutes_remaining < 0:
        return

    if minutes_remaining < 125:
        if last_streak_notification_diff < 125:
            return

        user_streak_count = user.day_streak
        if user_streak_count > 5:
            title = f'{user_streak_count} дней подряд и ВСЕ ЗРЯ?!'
        else:
            title = 'Ваша дневная серия под угрозой!'
        body = f'У вас осталось меньше двух часов, чтобы продлить ваш страйк!'

    elif minutes_remaining < 60 * 6 + 5:
        body = 'У вас осталось меньше 6-ти часов, чтобы продлить ваш страйк!'
        if last_streak_notification_diff < 60 * 6 + 5:
            return

    elif minutes_remaining < 60 * 24 + 5:
        title = 'Новый день - новые знания!'
        body = 'Позанимайтесь в приложении и продлите свою дневную серию!'

        if last_streak_notification_diff < 60 * 24 + 5:
            return

    send_notification_to_user(user, title, body, {'action': 'streak_notification'})
    notification_settings.last_streak_notification = timezone.now()
    notification_settings.save()


def send_friend_request_notification(user: UserModel, request_sender: UserModel):
    notification_settings: NotificationSettings = user.notification_settings
    if not notification_settings.friend_request_notification:
        return

    title = f'Новый друг?'
    description = f'{request_sender.name} хочет добавить вас в друзья'
    payload = {'action': 'friend_request', 'user_id': str(request_sender.id)}
    send_notification_to_user(user, title, description, payload)
