from django.urls import path, include
from rest_framework.routers import DefaultRouter

from job_portal.apps.chats.api.views import ChatRoomAPIViewSet

app_name = 'chats'

router = DefaultRouter()
router.register(r'api/v1/chats/rooms', ChatRoomAPIViewSet, basename='chat_rooms')

urlpatterns = [
    path('', include(router.urls)),
]
