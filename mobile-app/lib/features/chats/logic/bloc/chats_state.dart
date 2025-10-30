import '../../models/chat_model.dart';
import '../../models/chat_message_model.dart';

abstract class ChatsState {}

class ChatsInitialState extends ChatsState {}

class ChatsLoadingState extends ChatsState {}

class ChatsListLoadedState extends ChatsState {
  final List<ChatModel> chats;
  
  ChatsListLoadedState(this.chats);
}

class ChatsEmptyState extends ChatsState {
  final String message;
  
  ChatsEmptyState(this.message);
}

class ChatsErrorState extends ChatsState {
  final String message;
  
  ChatsErrorState(this.message);
}

class ChatMessagesLoadingState extends ChatsState {}

class ChatMessagesLoadedState extends ChatsState {
  final String chatId;
  final List<ChatMessageModel> messages;
  
  ChatMessagesLoadedState({required this.chatId, required this.messages});
}

class ChatMessagesEmptyState extends ChatsState {
  final String chatId;
  final String message;
  
  ChatMessagesEmptyState({required this.chatId, required this.message});
}

class ChatMessagesErrorState extends ChatsState {
  final String message;
  
  ChatMessagesErrorState(this.message);
}

class MessageSentState extends ChatsState {
  final ChatMessageModel message;
  
  MessageSentState(this.message);
}

