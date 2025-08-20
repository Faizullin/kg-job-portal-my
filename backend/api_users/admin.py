from django.contrib import admin
from backend.admin import UniversalAdmin
from .models import *

# @admin.register(Token)
# class TokenAdmin(UniversalAdmin):
#     list_display = ('user', 'key', 'created')
#     search_fields = ('user__email', 'key')
#     list_filter = ('user', 'created')

@admin.register(UserModel)
class UserModelAdmin(UniversalAdmin):
    filter_horizontal = ('friends', 'friendship_requests',)
    search_fields = ('name', 'email')

    def get_list_display(self, request):
        return 'name', 'email', 'blocked', 'user_type'


@admin.register(UserActivityDateModel)
class UserActivityDateModelAdmin(UniversalAdmin):
    list_display = ('user', 'datetime')
    list_filter = ('user', 'datetime')


@admin.register(UserPointAddHistory)
class UserPointAddHistoryAdmin(UniversalAdmin):
    list_display = ('user', 'points', 'description')


admin.site.register(NotificationSettings, UniversalAdmin)
admin.site.register(DeletedUsersModel, UniversalAdmin)