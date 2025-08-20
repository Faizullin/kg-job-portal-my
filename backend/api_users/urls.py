from django.urls import path
from .views import *

urlpatterns = [
    path('auth/', AuthViaFirebase.as_view()),
    path('get_user/', GetUserView.as_view()),
    path('update_timezone_difference/', UpdateTimezoneDifferenceView.as_view()),
    path("edit_photo/", EditPhotoView.as_view()),
    path("edit_user_data/", EditUserSettingsView.as_view()),
    path('update_day_streak/', UpdateDayStreak.as_view()),
    path('set_fcm_token/', SetFCMToken.as_view()),
    path('delete_account/', DeleteAccountView.as_view()),
    path('logout/', LogOutView.as_view()),

    # friends
    path('get_friends/', GetFriendsView.as_view()),
    path('search_friends/', SearchFriendsView.as_view()),  # Uses Pagination
    path('add_friend/', AddFriendView.as_view()),
    path('accept_friend/', AcceptFriendRequestView.as_view()),
    path('reject_friend/', DeclineFriendRequestView.as_view()),
    path('delete_friend/', DeleteFromFriendsView.as_view()),
]
