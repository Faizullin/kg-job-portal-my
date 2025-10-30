import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../logic/bloc/chats_bloc.dart';
import '../logic/bloc/chats_event.dart';
import '../logic/bloc/chats_state.dart';
import '../logic/data/chats_data_source.dart';
import '../logic/data/chats_repository.dart';
import '../models/chat_model.dart';
import '../models/chat_message_model.dart';

class ChatDetailScreen extends StatelessWidget {
  final ChatModel chat;

  const ChatDetailScreen({
    super.key,
    required this.chat,
  });

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => ChatsBloc(
        repository: ChatsRepositoryImpl(
          dataSource: ChatsDataSourceImpl(),
        ),
      )..add(LoadChatMessagesEvent(chat.id))
        ..add(MarkMessagesAsReadEvent(chat.id)),
      child: ChatDetailScreenView(chat: chat),
    );
  }
}

class ChatDetailScreenView extends StatefulWidget {
  final ChatModel chat;

  const ChatDetailScreenView({
    super.key,
    required this.chat,
  });

  @override
  State<ChatDetailScreenView> createState() => _ChatDetailScreenViewState();
}

class _ChatDetailScreenViewState extends State<ChatDetailScreenView> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ImagePicker _imagePicker = ImagePicker();
  List<MessageAttachment> _selectedAttachments = [];

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        title: Row(
          children: [
            Stack(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: Colors.grey[300],
                  child: widget.chat.userAvatar != null
                      ? ClipOval(
                          child: Image.network(
                            widget.chat.userAvatar!,
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => _buildAvatarPlaceholder(),
                          ),
                        )
                      : _buildAvatarPlaceholder(),
                ),
                if (widget.chat.isOnline)
                  Positioned(
                    right: 0,
                    bottom: 0,
                    child: Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: Colors.green,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.chat.userName,
                    style: GoogleFonts.roboto(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (widget.chat.isOnline)
                    Text(
                      'В сети',
                      style: GoogleFonts.roboto(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: BlocConsumer<ChatsBloc, ChatsState>(
              listener: (context, state) {
                if (state is ChatMessagesLoadedState) {
                  WidgetsBinding.instance.addPostFrameCallback((_) {
                    _scrollToBottom();
                  });
                }
              },
              builder: (context, state) {
                if (state is ChatMessagesLoadingState) {
                  return const Center(
                    child: CircularProgressIndicator(),
                  );
                }

                if (state is ChatMessagesErrorState) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'Ошибка',
                          style: GoogleFonts.roboto(fontSize: 18),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          state.message,
                          style: GoogleFonts.roboto(fontSize: 14, color: Colors.grey),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () {
                            context.read<ChatsBloc>().add(
                              LoadChatMessagesEvent(widget.chat.id),
                            );
                          },
                          child: const Text('Повторить'),
                        ),
                      ],
                    ),
                  );
                }

                if (state is ChatMessagesEmptyState) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.chat_bubble_outline, size: 64, color: Colors.grey[400]),
                        const SizedBox(height: 16),
                        Text(
                          state.message,
                          style: GoogleFonts.roboto(fontSize: 18, color: Colors.grey[600]),
                        ),
                      ],
                    ),
                  );
                }

                if (state is ChatMessagesLoadedState) {
                  return RefreshIndicator(
                    onRefresh: () async {
                      context.read<ChatsBloc>().add(
                        RefreshChatMessagesEvent(widget.chat.id),
                      );
                    },
                    child: ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      itemCount: state.messages.length,
                      itemBuilder: (context, index) {
                        final message = state.messages[index];
                        final isCurrentUser = message.senderId == 'current_user';
                        return _MessageBubble(
                          message: message,
                          isCurrentUser: isCurrentUser,
                        );
                      },
                    ),
                  );
                }

                return const SizedBox.shrink();
              },
            ),
          ),
          if (_selectedAttachments.isNotEmpty) _buildAttachmentPreview(),
          _MessageInputField(
            controller: _messageController,
            attachments: _selectedAttachments,
            onSend: (content) {
              if (content.trim().isNotEmpty || _selectedAttachments.isNotEmpty) {
                context.read<ChatsBloc>().add(
                  SendMessageEvent(
                    chatId: widget.chat.id,
                    content: content.trim(),
                    attachments: _selectedAttachments.isNotEmpty ? _selectedAttachments : null,
                  ),
                );
                _messageController.clear();
                setState(() {
                  _selectedAttachments = [];
                });
              }
            },
            onAttachImage: _pickImage,
            onAttachFile: _pickFile,
            onRemoveAttachment: (index) {
              setState(() {
                _selectedAttachments.removeAt(index);
              });
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAvatarPlaceholder() {
    return Icon(Icons.person, color: Colors.grey[600], size: 20);
  }

  Future<void> _pickImage() async {
    final pickedFile = await _imagePicker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _selectedAttachments.add(
          MessageAttachment(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            type: MessageAttachmentType.image,
            url: pickedFile.path,
            thumbnailUrl: pickedFile.path,
            fileName: pickedFile.name,
            mimeType: 'image/jpeg',
          ),
        );
      });
    }
  }

  Future<void> _pickFile() async {
    // In a real app, use file_picker package here
    // For now, we'll show a placeholder
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('File picker not implemented yet')),
    );
  }

  Widget _buildAttachmentPreview() {
    return Container(
      height: 100,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.grey[100],
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _selectedAttachments.length,
        itemBuilder: (context, index) {
          final attachment = _selectedAttachments[index];
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: Stack(
              children: [
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    color: Colors.white,
                  ),
                  child: attachment.type == MessageAttachmentType.image
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.file(
                            File(attachment.url),
                            fit: BoxFit.cover,
                          ),
                        )
                      : Icon(Icons.insert_drive_file, size: 40),
                ),
                Positioned(
                  top: -5,
                  right: -5,
                  child: IconButton(
                    icon: const Icon(Icons.close, size: 20),
                    color: Colors.red,
                    onPressed: () {
                      setState(() {
                        _selectedAttachments.removeAt(index);
                      });
                    },
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final ChatMessageModel message;
  final bool isCurrentUser;

  const _MessageBubble({
    required this.message,
    required this.isCurrentUser,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        mainAxisAlignment: isCurrentUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isCurrentUser)
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.grey[300],
              child: message.senderAvatar != null
                  ? ClipOval(
                      child: Image.network(
                        message.senderAvatar!,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => Icon(Icons.person, size: 16),
                      ),
                    )
                  : Icon(Icons.person, size: 16, color: Colors.grey[600]),
            ),
          if (!isCurrentUser) const SizedBox(width: 8),
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: isCurrentUser ? const Color(0xFF2563EB) : Colors.grey[200],
                borderRadius: BorderRadius.circular(18),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (message.attachments != null && message.attachments!.isNotEmpty)
                    ...message.attachments!.map((attachment) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: _buildAttachmentView(attachment, isCurrentUser),
                      );
                    }).toList(),
                  if (message.content.isNotEmpty) ...[
                    Text(
                      message.content,
                      style: GoogleFonts.roboto(
                        fontSize: 15,
                        color: isCurrentUser ? Colors.white : Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 4),
                  ],
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        _formatTime(message.createdAt),
                        style: GoogleFonts.roboto(
                          fontSize: 11,
                          color: isCurrentUser ? Colors.white70 : Colors.grey[600],
                        ),
                      ),
                      if (isCurrentUser) ...[
                        const SizedBox(width: 4),
                        _buildMessageStatusIcon(message),
                      ],
                    ],
                  ),
                ],
              ),
            ),
          ),
          if (isCurrentUser) const SizedBox(width: 8),
        ],
      ),
    );
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }

  Widget _buildMessageStatusIcon(ChatMessageModel message) {
    if (message.status == MessageStatus.sending) {
      return const SizedBox(
        width: 14,
        height: 14,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(Colors.white70),
        ),
      );
    }
    return Icon(
      message.status == MessageStatus.read || message.isRead
          ? Icons.done_all
          : message.status == MessageStatus.delivered
              ? Icons.done_all
              : Icons.done,
      size: 14,
      color: (message.status == MessageStatus.read || message.isRead)
          ? Colors.blue[200]
          : Colors.white70,
    );
  }

  Widget _buildAttachmentView(MessageAttachment attachment, bool isCurrentUser) {
    if (attachment.type == MessageAttachmentType.image) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: Image.file(
          File(attachment.url),
          width: 200,
          height: 200,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return Container(
              width: 200,
              height: 200,
              color: Colors.grey[300],
              child: const Icon(Icons.broken_image, size: 50),
            );
          },
        ),
      );
    } else {
      return Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isCurrentUser ? Colors.white.withOpacity(0.2) : Colors.grey[300],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.insert_drive_file,
              size: 24,
              color: isCurrentUser ? Colors.white : Colors.black87,
            ),
            const SizedBox(width: 8),
            Flexible(
              child: Text(
                attachment.fileName,
                style: GoogleFonts.roboto(
                  fontSize: 14,
                  color: isCurrentUser ? Colors.white : Colors.black87,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      );
    }
  }
}

class _MessageInputField extends StatelessWidget {
  final TextEditingController controller;
  final Function(String) onSend;
  final List<MessageAttachment> attachments;
  final VoidCallback onAttachImage;
  final VoidCallback onAttachFile;
  final Function(int) onRemoveAttachment;

  const _MessageInputField({
    required this.controller,
    required this.onSend,
    this.attachments = const [],
    required this.onAttachImage,
    required this.onAttachFile,
    required this.onRemoveAttachment,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            IconButton(
              icon: const Icon(Icons.attach_file, color: Color(0xFF2563EB)),
              onPressed: onAttachFile,
            ),
            IconButton(
              icon: const Icon(Icons.image, color: Color(0xFF2563EB)),
              onPressed: onAttachImage,
            ),
            Expanded(
              child: TextField(
                controller: controller,
                decoration: InputDecoration(
                  hintText: 'Написать сообщение...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide(color: Colors.grey[300]!),
                  ),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                ),
                maxLines: null,
                textInputAction: TextInputAction.send,
                onSubmitted: onSend,
              ),
            ),
            const SizedBox(width: 4),
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFF2563EB),
                shape: BoxShape.circle,
              ),
              child: IconButton(
                icon: const Icon(Icons.send, color: Colors.white, size: 20),
                onPressed: () => onSend(controller.text),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

