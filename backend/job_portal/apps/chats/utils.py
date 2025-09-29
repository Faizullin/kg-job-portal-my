from .models import ChatRoom


def get_chat_channel_name(chat_room: ChatRoom | int) -> str:
    """Generate channel name for WebSocket group."""

    if isinstance(chat_room, ChatRoom):
        chat_room_id = chat_room.id
    else:
        chat_room_id = chat_room
    return f"chat_{chat_room_id}"
