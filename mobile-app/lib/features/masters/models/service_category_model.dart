/// Модель категории услуг
class ServiceCategoryModel {
  final String id;
  final String title;
  final String imageUrl;
  final String backgroundColor;
  final bool isActive;
  final int masterCount;
  final DateTime createdAt;

  const ServiceCategoryModel({
    required this.id,
    required this.title,
    required this.imageUrl,
    required this.backgroundColor,
    required this.isActive,
    required this.masterCount,
    required this.createdAt,
  });

  /// Создание из JSON
  factory ServiceCategoryModel.fromJson(Map<String, dynamic> json) {
    return ServiceCategoryModel(
      id: json['id'] as String,
      title: json['title'] as String,
      imageUrl: json['image_url'] as String,
      backgroundColor: json['background_color'] as String,
      isActive: json['is_active'] as bool,
      masterCount: json['master_count'] as int,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  /// Конвертация в JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'image_url': imageUrl,
      'background_color': backgroundColor,
      'is_active': isActive,
      'master_count': masterCount,
      'created_at': createdAt.toIso8601String(),
    };
  }

  /// Копирование с изменениями
  ServiceCategoryModel copyWith({
    String? id,
    String? title,
    String? imageUrl,
    String? backgroundColor,
    bool? isActive,
    int? masterCount,
    DateTime? createdAt,
  }) {
    return ServiceCategoryModel(
      id: id ?? this.id,
      title: title ?? this.title,
      imageUrl: imageUrl ?? this.imageUrl,
      backgroundColor: backgroundColor ?? this.backgroundColor,
      isActive: isActive ?? this.isActive,
      masterCount: masterCount ?? this.masterCount,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ServiceCategoryModel &&
        other.id == id &&
        other.title == title &&
        other.backgroundColor == backgroundColor;
  }

  @override
  int get hashCode {
    return Object.hash(id, title, backgroundColor);
  }

  @override
  String toString() {
    return 'ServiceCategoryModel(id: $id, title: $title, backgroundColor: $backgroundColor)';
  }
}
