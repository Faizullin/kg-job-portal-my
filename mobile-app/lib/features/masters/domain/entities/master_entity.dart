import 'package:equatable/equatable.dart';

/// Сущность мастера (Domain слой)
class MasterEntity extends Equatable {
  final String id;
  final String name;
  final String? avatarUrl;
  final String? description;
  final double rating;
  final int reviewsCount;
  final List<String> specializations;
  final String? location;
  final bool isOnline;
  final DateTime? lastSeen;
  final List<String> images;
  final Map<String, dynamic>? additionalInfo;

  const MasterEntity({
    required this.id,
    required this.name,
    this.avatarUrl,
    this.description,
    required this.rating,
    required this.reviewsCount,
    required this.specializations,
    this.location,
    required this.isOnline,
    this.lastSeen,
    required this.images,
    this.additionalInfo,
  });

  @override
  List<Object?> get props => [
        id,
        name,
        avatarUrl,
        description,
        rating,
        reviewsCount,
        specializations,
        location,
        isOnline,
        lastSeen,
        images,
        additionalInfo,
      ];

  /// Копирование с изменениями
  MasterEntity copyWith({
    String? id,
    String? name,
    String? avatarUrl,
    String? description,
    double? rating,
    int? reviewsCount,
    List<String>? specializations,
    String? location,
    bool? isOnline,
    DateTime? lastSeen,
    List<String>? images,
    Map<String, dynamic>? additionalInfo,
  }) {
    return MasterEntity(
      id: id ?? this.id,
      name: name ?? this.name,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      description: description ?? this.description,
      rating: rating ?? this.rating,
      reviewsCount: reviewsCount ?? this.reviewsCount,
      specializations: specializations ?? this.specializations,
      location: location ?? this.location,
      isOnline: isOnline ?? this.isOnline,
      lastSeen: lastSeen ?? this.lastSeen,
      images: images ?? this.images,
      additionalInfo: additionalInfo ?? this.additionalInfo,
    );
  }

  @override
  String toString() {
    return 'MasterEntity(id: $id, name: $name, rating: $rating, reviewsCount: $reviewsCount)';
  }
}
