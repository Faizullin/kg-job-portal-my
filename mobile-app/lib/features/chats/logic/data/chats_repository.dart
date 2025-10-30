import 'package:dartz/dartz.dart';
import '../../models/chat_model.dart';
import '../../models/chat_message_model.dart';
import 'chats_data_source.dart';

abstract class ChatsRepository {
  Future<Either<String, List<ChatModel>>> getChatList();
  Future<Either<String, List<ChatMessageModel>>> getChatMessages(String chatId);
  Future<Either<String, ChatMessageModel>> sendMessage(String chatId, String content);
  Future<Either<String, bool>> markMessagesAsRead(String chatId);
}

class ChatsRepositoryImpl implements ChatsRepository {
  final ChatsDataSource _dataSource;

  ChatsRepositoryImpl({
    required ChatsDataSource dataSource,
  }) : _dataSource = dataSource;

  @override
  Future<Either<String, List<ChatModel>>> getChatList() async {
    try {
      final chats = await _dataSource.getChatList();
      return Right(chats);
    } catch (e) {
      return Left('Ошибка загрузки списка чатов: ${e.toString()}');
    }
  }

  @override
  Future<Either<String, List<ChatMessageModel>>> getChatMessages(String chatId) async {
    try {
      final messages = await _dataSource.getChatMessages(chatId);
      return Right(messages);
    } catch (e) {
      return Left('Ошибка загрузки сообщений: ${e.toString()}');
    }
  }

  @override
  Future<Either<String, ChatMessageModel>> sendMessage(String chatId, String content) async {
    try {
      final message = await _dataSource.sendMessage(chatId, content);
      return Right(message);
    } catch (e) {
      return Left('Ошибка отправки сообщения: ${e.toString()}');
    }
  }

  @override
  Future<Either<String, bool>> markMessagesAsRead(String chatId) async {
    try {
      final result = await _dataSource.markMessagesAsRead(chatId);
      return Right(result);
    } catch (e) {
      return Left('Ошибка отметки сообщений как прочитанных: ${e.toString()}');
    }
  }
}

