import '../../models/chat_message_model.dart';

abstract class ChatsEvent {}

class LoadChatListEvent extends ChatsEvent {}

class RefreshChatListEvent extends ChatsEvent {}

class LoadChatMessagesEvent extends ChatsEvent {
  final String chatId;
  
  LoadChatMessagesEvent(this.chatId);
}

class RefreshChatMessagesEvent extends ChatsEvent {
  final String chatId;
  
  RefreshChatMessagesEvent(this.chatId);
}

class SendMessageEvent extends ChatsEvent {
  final String chatId;
  final String content;
  final List<MessageAttachment>? attachments;
  
  SendMessageEvent({
    required this.chatId,
    required this.content,
    this.attachments,
  });
}

class MarkMessagesAsReadEvent extends ChatsEvent {
  final String chatId;
  
  MarkMessagesAsReadEvent(this.chatId);
}

