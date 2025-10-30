/// Модель мастера
class MasterModel {
  final String id;
  final String name;
  final String specialty;
  final double rating;
  final int reviewCount;
  final String location;
  final bool isOnline;
  final int completedJobs;
  final String hourlyRate;
  final String responseTime;
  final List<String> skills;
  final List<String> portfolioImages;
  final String? avatarUrl;
  final DateTime createdAt;
  final DateTime updatedAt;

  const MasterModel({
    required this.id,
    required this.name,
    required this.specialty,
    required this.rating,
    required this.reviewCount,
    required this.location,
    required this.isOnline,
    required this.completedJobs,
    required this.hourlyRate,
    required this.responseTime,
    required this.skills,
    required this.portfolioImages,
    this.avatarUrl,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Создание из JSON
  factory MasterModel.fromJson(Map<String, dynamic> json) {
    return MasterModel(
      id: json['id'] as String,
      name: json['name'] as String,
      specialty: json['specialty'] as String,
      rating: (json['rating'] as num).toDouble(),
      reviewCount: json['review_count'] as int,
      location: json['location'] as String,
      isOnline: json['is_online'] as bool,
      completedJobs: json['completed_jobs'] as int,
      hourlyRate: json['hourly_rate'] as String,
      responseTime: json['response_time'] as String,
      skills: List<String>.from(json['skills'] as List),
      portfolioImages: List<String>.from(json['portfolio_images'] as List),
      avatarUrl: json['avatar_url'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  /// Конвертация в JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'specialty': specialty,
      'rating': rating,
      'review_count': reviewCount,
      'location': location,
      'is_online': isOnline,
      'completed_jobs': completedJobs,
      'hourly_rate': hourlyRate,
      'response_time': responseTime,
      'skills': skills,
      'portfolio_images': portfolioImages,
      'avatar_url': avatarUrl,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// Копирование с изменениями
  MasterModel copyWith({
    String? id,
    String? name,
    String? specialty,
    double? rating,
    int? reviewCount,
    String? location,
    bool? isOnline,
    int? completedJobs,
    String? hourlyRate,
    String? responseTime,
    List<String>? skills,
    List<String>? portfolioImages,
    String? avatarUrl,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return MasterModel(
      id: id ?? this.id,
      name: name ?? this.name,
      specialty: specialty ?? this.specialty,
      rating: rating ?? this.rating,
      reviewCount: reviewCount ?? this.reviewCount,
      location: location ?? this.location,
      isOnline: isOnline ?? this.isOnline,
      completedJobs: completedJobs ?? this.completedJobs,
      hourlyRate: hourlyRate ?? this.hourlyRate,
      responseTime: responseTime ?? this.responseTime,
      skills: skills ?? this.skills,
      portfolioImages: portfolioImages ?? this.portfolioImages,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is MasterModel &&
        other.id == id &&
        other.name == name &&
        other.specialty == specialty &&
        other.rating == rating;
  }

  @override
  int get hashCode {
    return Object.hash(id, name, specialty, rating);
  }

  @override
  String toString() {
    return 'MasterModel(id: $id, name: $name, specialty: $specialty, rating: $rating)';
  }
}
