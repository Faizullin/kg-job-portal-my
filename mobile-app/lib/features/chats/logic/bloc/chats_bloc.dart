import 'package:flutter_bloc/flutter_bloc.dart';
import '../data/chats_repository.dart';
import '../../models/chat_model.dart';
import '../../models/chat_message_model.dart';
import 'chats_event.dart';
import 'chats_state.dart';

class ChatsBloc extends Bloc<ChatsEvent, ChatsState> {
  final ChatsRepository _repository;
  String? _currentChatId;
  List<ChatMessageModel> _currentMessages = [];

  ChatsBloc({
    required ChatsRepository repository,
  }) : _repository = repository, super(ChatsInitialState()) {
    on<LoadChatListEvent>(_onLoadChatList);
    on<RefreshChatListEvent>(_onRefreshChatList);
    on<LoadChatMessagesEvent>(_onLoadChatMessages);
    on<RefreshChatMessagesEvent>(_onRefreshChatMessages);
    on<SendMessageEvent>(_onSendMessage);
    on<MarkMessagesAsReadEvent>(_onMarkMessagesAsRead);
  }

  Future<void> _onLoadChatList(
    LoadChatListEvent event,
    Emitter<ChatsState> emit,
  ) async {
    emit(ChatsLoadingState());

    final result = await _repository.getChatList();
    
    result.fold(
      (error) => emit(ChatsErrorState(error)),
      (chats) {
        if (chats.isEmpty) {
          emit(ChatsEmptyState('У вас пока нет сообщений'));
        } else {
          emit(ChatsListLoadedState(chats));
        }
      },
    );
  }

  Future<void> _onRefreshChatList(
    RefreshChatListEvent event,
    Emitter<ChatsState> emit,
  ) async {
    final result = await _repository.getChatList();
    
    result.fold(
      (error) => emit(ChatsErrorState(error)),
      (chats) {
        if (chats.isEmpty) {
          emit(ChatsEmptyState('У вас пока нет сообщений'));
        } else {
          emit(ChatsListLoadedState(chats));
        }
      },
    );
  }

  Future<void> _onLoadChatMessages(
    LoadChatMessagesEvent event,
    Emitter<ChatsState> emit,
  ) async {
    _currentChatId = event.chatId;
    emit(ChatMessagesLoadingState());

    final result = await _repository.getChatMessages(event.chatId);
    
    result.fold(
      (error) => emit(ChatMessagesErrorState(error)),
      (messages) {
        _currentMessages = messages;
        if (messages.isEmpty) {
          emit(ChatMessagesEmptyState(
            chatId: event.chatId,
            message: 'Начните разговор',
          ));
        } else {
          emit(ChatMessagesLoadedState(
            chatId: event.chatId,
            messages: messages,
          ));
        }
      },
    );
  }

  Future<void> _onRefreshChatMessages(
    RefreshChatMessagesEvent event,
    Emitter<ChatsState> emit,
  ) async {
    final result = await _repository.getChatMessages(event.chatId);
    
    result.fold(
      (error) => emit(ChatMessagesErrorState(error)),
      (messages) {
        _currentMessages = messages;
        emit(ChatMessagesLoadedState(
          chatId: event.chatId,
          messages: messages,
        ));
      },
    );
  }

  Future<void> _onSendMessage(
    SendMessageEvent event,
    Emitter<ChatsState> emit,
  ) async {
    final tempMessage = ChatMessageModel(
      id: 'temp_${DateTime.now().millisecondsSinceEpoch}',
      chatId: event.chatId,
      senderId: 'current_user',
      senderName: 'Вы',
      content: event.content,
      createdAt: DateTime.now(),
      status: MessageStatus.sending,
      attachments: event.attachments,
    );

    _currentMessages = [..._currentMessages, tempMessage];
    emit(ChatMessagesLoadedState(
      chatId: event.chatId,
      messages: _currentMessages,
    ));

    final result = await _repository.sendMessage(event.chatId, event.content);
    
    result.fold(
      (error) {
        _currentMessages = _currentMessages.where((m) => m.id != tempMessage.id).toList();
        emit(ChatMessagesErrorState(error));
        if (state is ChatMessagesLoadedState) {
          emit(ChatMessagesLoadedState(
            chatId: event.chatId,
            messages: _currentMessages,
          ));
        }
      },
      (message) {
        final index = _currentMessages.indexWhere((m) => m.id == tempMessage.id);
        if (index >= 0) {
          _currentMessages[index] = message.copyWith(status: MessageStatus.sent);
        } else {
          _currentMessages = [..._currentMessages, message.copyWith(status: MessageStatus.sent)];
        }
        emit(ChatMessagesLoadedState(
          chatId: event.chatId,
          messages: _currentMessages,
        ));
      },
    );
  }

  Future<void> _onMarkMessagesAsRead(
    MarkMessagesAsReadEvent event,
    Emitter<ChatsState> emit,
  ) async {
    final result = await _repository.markMessagesAsRead(event.chatId);
    
    result.fold(
      (error) => emit(ChatMessagesErrorState(error)),
      (success) {
        if (_currentChatId == event.chatId && state is ChatMessagesLoadedState) {
          final currentState = state as ChatMessagesLoadedState;
          final updatedMessages = currentState.messages.map((msg) {
            return msg.copyWith(isRead: true);
          }).toList();
          emit(ChatMessagesLoadedState(
            chatId: event.chatId,
            messages: updatedMessages,
          ));
        }
      },
    );
  }
}

