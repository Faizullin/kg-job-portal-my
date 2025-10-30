enum MessageStatus {
  sending,
  sent,
  delivered,
  read,
}

enum MessageAttachmentType {
  image,
  file,
  document,
}

class MessageAttachment {
  final String id;
  final MessageAttachmentType type;
  final String url;
  final String? thumbnailUrl;
  final String fileName;
  final int? fileSize;
  final String? mimeType;

  const MessageAttachment({
    required this.id,
    required this.type,
    required this.url,
    this.thumbnailUrl,
    required this.fileName,
    this.fileSize,
    this.mimeType,
  });
}

class ChatMessageModel {
  final String id;
  final String chatId;
  final String senderId;
  final String senderName;
  final String? senderAvatar;
  final String content;
  final DateTime createdAt;
  final bool isRead;
  final String? messageType;
  final Map<String, dynamic>? metadata;
  final MessageStatus? status;
  final List<MessageAttachment>? attachments;

  const ChatMessageModel({
    required this.id,
    required this.chatId,
    required this.senderId,
    required this.senderName,
    this.senderAvatar,
    required this.content,
    required this.createdAt,
    this.isRead = false,
    this.messageType,
    this.metadata,
    this.status,
    this.attachments,
  });

  factory ChatMessageModel.fromJson(Map<String, dynamic> json) {
    List<MessageAttachment>? attachments;
    if (json['attachments'] != null) {
      attachments = (json['attachments'] as List)
          .map((a) => MessageAttachment(
                id: a['id'] as String,
                type: MessageAttachmentType.values.firstWhere(
                  (e) => e.name == a['type'],
                  orElse: () => MessageAttachmentType.file,
                ),
                url: a['url'] as String,
                thumbnailUrl: a['thumbnail_url'] as String?,
                fileName: a['file_name'] as String,
                fileSize: a['file_size'] as int?,
                mimeType: a['mime_type'] as String?,
              ))
          .toList();
    }

    return ChatMessageModel(
      id: json['id'] as String,
      chatId: json['chat_id'] as String,
      senderId: json['sender_id'] as String,
      senderName: json['sender_name'] as String,
      senderAvatar: json['sender_avatar'] as String?,
      content: json['content'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      isRead: json['is_read'] as bool? ?? false,
      messageType: json['message_type'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      status: json['status'] != null
          ? MessageStatus.values.firstWhere(
              (e) => e.name == json['status'],
              orElse: () => MessageStatus.sent,
            )
          : null,
      attachments: attachments,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'chat_id': chatId,
      'sender_id': senderId,
      'sender_name': senderName,
      'sender_avatar': senderAvatar,
      'content': content,
      'created_at': createdAt.toIso8601String(),
      'is_read': isRead,
      'message_type': messageType,
      'metadata': metadata,
      'status': status?.name,
      'attachments': attachments?.map((a) => {
            'id': a.id,
            'type': a.type.name,
            'url': a.url,
            'thumbnail_url': a.thumbnailUrl,
            'file_name': a.fileName,
            'file_size': a.fileSize,
            'mime_type': a.mimeType,
          }).toList(),
    };
  }

  ChatMessageModel copyWith({
    String? id,
    String? chatId,
    String? senderId,
    String? senderName,
    String? senderAvatar,
    String? content,
    DateTime? createdAt,
    bool? isRead,
    String? messageType,
    Map<String, dynamic>? metadata,
    MessageStatus? status,
    List<MessageAttachment>? attachments,
  }) {
    return ChatMessageModel(
      id: id ?? this.id,
      chatId: chatId ?? this.chatId,
      senderId: senderId ?? this.senderId,
      senderName: senderName ?? this.senderName,
      senderAvatar: senderAvatar ?? this.senderAvatar,
      content: content ?? this.content,
      createdAt: createdAt ?? this.createdAt,
      isRead: isRead ?? this.isRead,
      messageType: messageType ?? this.messageType,
      metadata: metadata ?? this.metadata,
      status: status ?? this.status,
      attachments: attachments ?? this.attachments,
    );
  }
}

