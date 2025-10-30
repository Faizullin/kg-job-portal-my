/// Модель задачи
class TaskModel {
  final String id;
  final String title;
  final String description;
  final String status; // 'pending', 'in_progress', 'completed', 'cancelled'
  final String priority; // 'low', 'medium', 'high'
  final String? masterId;
  final String? masterName;
  final String? clientId;
  final String? clientName;
  final String location;
  final String category;
  final double? estimatedPrice;
  final double? finalPrice;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? scheduledDate;
  final DateTime? completedDate;

  const TaskModel({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.priority,
    this.masterId,
    this.masterName,
    this.clientId,
    this.clientName,
    required this.location,
    required this.category,
    this.estimatedPrice,
    this.finalPrice,
    required this.createdAt,
    required this.updatedAt,
    this.scheduledDate,
    this.completedDate,
  });

  /// Создание из JSON
  factory TaskModel.fromJson(Map<String, dynamic> json) {
    return TaskModel(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      status: json['status'] as String,
      priority: json['priority'] as String,
      masterId: json['master_id'] as String?,
      masterName: json['master_name'] as String?,
      clientId: json['client_id'] as String?,
      clientName: json['client_name'] as String?,
      location: json['location'] as String,
      category: json['category'] as String,
      estimatedPrice: json['estimated_price'] != null ? (json['estimated_price'] as num).toDouble() : null,
      finalPrice: json['final_price'] != null ? (json['final_price'] as num).toDouble() : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      scheduledDate: json['scheduled_date'] != null ? DateTime.parse(json['scheduled_date'] as String) : null,
      completedDate: json['completed_date'] != null ? DateTime.parse(json['completed_date'] as String) : null,
    );
  }

  /// Конвертация в JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'status': status,
      'priority': priority,
      'master_id': masterId,
      'master_name': masterName,
      'client_id': clientId,
      'client_name': clientName,
      'location': location,
      'category': category,
      'estimated_price': estimatedPrice,
      'final_price': finalPrice,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'scheduled_date': scheduledDate?.toIso8601String(),
      'completed_date': completedDate?.toIso8601String(),
    };
  }

  /// Копирование с изменениями
  TaskModel copyWith({
    String? id,
    String? title,
    String? description,
    String? status,
    String? priority,
    String? masterId,
    String? masterName,
    String? clientId,
    String? clientName,
    String? location,
    String? category,
    double? estimatedPrice,
    double? finalPrice,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? scheduledDate,
    DateTime? completedDate,
  }) {
    return TaskModel(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      status: status ?? this.status,
      priority: priority ?? this.priority,
      masterId: masterId ?? this.masterId,
      masterName: masterName ?? this.masterName,
      clientId: clientId ?? this.clientId,
      clientName: clientName ?? this.clientName,
      location: location ?? this.location,
      category: category ?? this.category,
      estimatedPrice: estimatedPrice ?? this.estimatedPrice,
      finalPrice: finalPrice ?? this.finalPrice,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      scheduledDate: scheduledDate ?? this.scheduledDate,
      completedDate: completedDate ?? this.completedDate,
    );
  }

  /// Получение статуса на русском языке
  String get statusDisplayName {
    switch (status) {
      case 'pending':
        return 'В ожидании';
      case 'in_progress':
        return 'В работе';
      case 'completed':
        return 'Завершена';
      case 'cancelled':
        return 'Отменена';
      default:
        return 'Неизвестно';
    }
  }

  /// Получение приоритета на русском языке
  String get priorityDisplayName {
    switch (priority) {
      case 'low':
        return 'Низкий';
      case 'medium':
        return 'Средний';
      case 'high':
        return 'Высокий';
      default:
        return 'Неизвестно';
    }
  }

  /// Получение цвета статуса
  String get statusColor {
    switch (status) {
      case 'pending':
        return '0xFFFFA500'; // Orange
      case 'in_progress':
        return '0xFF007AFF'; // Blue
      case 'completed':
        return '0xFF34C759'; // Green
      case 'cancelled':
        return '0xFFFF3B30'; // Red
      default:
        return '0xFF8E8E93'; // Gray
    }
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is TaskModel &&
        other.id == id &&
        other.title == title &&
        other.status == status;
  }

  @override
  int get hashCode {
    return Object.hash(id, title, status);
  }

  @override
  String toString() {
    return 'TaskModel(id: $id, title: $title, status: $status)';
  }
}
