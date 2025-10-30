import '../../models/chat_model.dart';
import '../../models/chat_message_model.dart';

abstract class ChatsDataSource {
  Future<List<ChatModel>> getChatList();
  Future<List<ChatMessageModel>> getChatMessages(String chatId);
  Future<ChatMessageModel> sendMessage(String chatId, String content);
  Future<bool> markMessagesAsRead(String chatId);
}

class ChatsDataSourceImpl implements ChatsDataSource {
  @override
  Future<List<ChatModel>> getChatList() async {
    await Future.delayed(const Duration(milliseconds: 800));
    
    return [
      ChatModel(
        id: '1',
        userId: 'user_1',
        userName: 'Алексей Петров',
        userAvatar: null,
        lastMessage: 'Привет! Интересует ваша вакансия...',
        lastMessageTime: DateTime.now().subtract(const Duration(minutes: 5)),
        unreadCount: 2,
        isOnline: true,
      ),
      ChatModel(
        id: '2',
        userId: 'user_2',
        userName: 'Мария Иванова',
        userAvatar: null,
        lastMessage: 'Спасибо за отклик',
        lastMessageTime: DateTime.now().subtract(const Duration(hours: 2)),
        unreadCount: 0,
        isOnline: false,
      ),
      ChatModel(
        id: '3',
        userId: 'user_3',
        userName: 'Дмитрий Смирнов',
        userAvatar: null,
        lastMessage: 'Когда можно начать работу?',
        lastMessageTime: DateTime.now().subtract(const Duration(days: 1)),
        unreadCount: 1,
        isOnline: true,
      ),
    ];
  }

  @override
  Future<List<ChatMessageModel>> getChatMessages(String chatId) async {
    await Future.delayed(const Duration(milliseconds: 600));
    
    return [
      ChatMessageModel(
        id: '1',
        chatId: chatId,
        senderId: 'user_1',
        senderName: 'Алексей Петров',
        senderAvatar: null,
        content: 'Здравствуйте! Меня интересует ваша вакансия.',
        createdAt: DateTime.now().subtract(const Duration(hours: 2)),
        isRead: true,
      ),
      ChatMessageModel(
        id: '2',
        chatId: chatId,
        senderId: 'current_user',
        senderName: 'Вы',
        senderAvatar: null,
        content: 'Здравствуйте! Рады вашей заинтересованности.',
        createdAt: DateTime.now().subtract(const Duration(hours: 1, minutes: 45)),
        isRead: true,
      ),
      ChatMessageModel(
        id: '3',
        chatId: chatId,
        senderId: 'user_1',
        senderName: 'Алексей Петров',
        senderAvatar: null,
        content: 'Можно ли узнать больше о требованиях?',
        createdAt: DateTime.now().subtract(const Duration(minutes: 30)),
        isRead: false,
      ),
      ChatMessageModel(
        id: '4',
        chatId: chatId,
        senderId: 'user_1',
        senderName: 'Алексей Петров',
        senderAvatar: null,
        content: 'Привет! Интересует ваша вакансия...',
        createdAt: DateTime.now().subtract(const Duration(minutes: 5)),
        isRead: false,
      ),
    ];
  }

  @override
  Future<ChatMessageModel> sendMessage(String chatId, String content) async {
    await Future.delayed(const Duration(milliseconds: 300));
    
    return ChatMessageModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      chatId: chatId,
      senderId: 'current_user',
      senderName: 'Вы',
      senderAvatar: null,
      content: content,
      createdAt: DateTime.now(),
      isRead: false,
    );
  }

  @override
  Future<bool> markMessagesAsRead(String chatId) async {
    await Future.delayed(const Duration(milliseconds: 200));
    return true;
  }
}

