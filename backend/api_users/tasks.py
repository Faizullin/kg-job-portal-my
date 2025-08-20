from .models import UserActivityDateModel, UserModel
from .cloud_messaging import *


def check_for_strike():
    """
    Check if user has a strike and send a notification if needed
    """
    # get all users that have at least one UserActivityDateModel object
    users = UserModel.objects.filter(activity_dates__isnull=False).distinct()
    for user in users:
        user: UserModel
        remaining_hours = user.remaining_hours_till_streak_reset()
        if 0 <= remaining_hours <= 24:
            send_streak_notification(user=user, minutes_remaining=remaining_hours * 60)

    return True
