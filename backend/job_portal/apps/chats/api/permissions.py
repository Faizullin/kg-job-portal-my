from rest_framework import permissions

from ..models import ChatParticipant


class IsChatParticipant(permissions.BasePermission):
    """
    Permission to check if user is a participant in the chat room.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'chat_room'):
            return obj.chat_room.participants.filter(id=request.user.id).exists()

        # For ChatRoom objects
        if hasattr(obj, 'participants'):
            return obj.participants.filter(id=request.user.id).exists()

        return False


class IsChatRoomAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin of the chat room.
    """

    def has_object_permission(self, request, view, obj):
        # Safe methods allowed for all participants
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user is admin
        try:
            participant = ChatParticipant.objects.get(
                chat_room=obj if hasattr(obj, 'participants') else obj.chat_room,
                user=request.user
            )
            return participant.role == 'admin'
        except ChatParticipant.DoesNotExist:
            return False


class IsMessageSender(permissions.BasePermission):
    """
    Permission to check if user is the sender of the message.
    """

    def has_object_permission(self, request, view, obj):
        # Safe methods allowed for all participants
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only sender can modify their own messages
        return obj.sender == request.user
