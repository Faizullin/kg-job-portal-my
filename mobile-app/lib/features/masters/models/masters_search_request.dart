/// Запрос поиска мастеров
class MastersSearchRequest {
  final String? query;
  final String? categoryId;
  final String? location;
  final double? minRating;
  final int? maxHourlyRate;
  final bool? isOnline;
  final String? sortBy; // 'rating', 'price', 'distance'
  final int page;
  final int limit;

  const MastersSearchRequest({
    this.query,
    this.categoryId,
    this.location,
    this.minRating,
    this.maxHourlyRate,
    this.isOnline,
    this.sortBy,
    this.page = 1,
    this.limit = 20,
  });

  /// Создание из JSON
  factory MastersSearchRequest.fromJson(Map<String, dynamic> json) {
    return MastersSearchRequest(
      query: json['query'] as String?,
      categoryId: json['category_id'] as String?,
      location: json['location'] as String?,
      minRating: json['min_rating'] != null ? (json['min_rating'] as num).toDouble() : null,
      maxHourlyRate: json['max_hourly_rate'] as int?,
      isOnline: json['is_online'] as bool?,
      sortBy: json['sort_by'] as String?,
      page: json['page'] as int? ?? 1,
      limit: json['limit'] as int? ?? 20,
    );
  }

  /// Конвертация в JSON
  Map<String, dynamic> toJson() {
    return {
      'query': query,
      'category_id': categoryId,
      'location': location,
      'min_rating': minRating,
      'max_hourly_rate': maxHourlyRate,
      'is_online': isOnline,
      'sort_by': sortBy,
      'page': page,
      'limit': limit,
    };
  }

  /// Валидация запроса
  Map<String, String> validate() {
    final errors = <String, String>{};

    if (query != null && query!.trim().length < 2) {
      errors['query'] = 'Поисковый запрос должен содержать минимум 2 символа';
    }

    if (minRating != null && (minRating! < 1 || minRating! > 5)) {
      errors['min_rating'] = 'Рейтинг должен быть от 1 до 5';
    }

    if (maxHourlyRate != null && maxHourlyRate! < 0) {
      errors['max_hourly_rate'] = 'Максимальная ставка не может быть отрицательной';
    }

    if (page < 1) {
      errors['page'] = 'Номер страницы должен быть больше 0';
    }

    if (limit < 1 || limit > 100) {
      errors['limit'] = 'Лимит должен быть от 1 до 100';
    }

    return errors;
  }

  /// Создание запроса для поиска по тексту
  factory MastersSearchRequest.search(String query) {
    return MastersSearchRequest(query: query);
  }

  /// Создание запроса для фильтрации по категории
  factory MastersSearchRequest.byCategory(String categoryId) {
    return MastersSearchRequest(categoryId: categoryId);
  }

  /// Создание запроса для фильтрации по локации
  factory MastersSearchRequest.byLocation(String location) {
    return MastersSearchRequest(location: location);
  }

  /// Копирование с изменениями
  MastersSearchRequest copyWith({
    String? query,
    String? categoryId,
    String? location,
    double? minRating,
    int? maxHourlyRate,
    bool? isOnline,
    String? sortBy,
    int? page,
    int? limit,
  }) {
    return MastersSearchRequest(
      query: query ?? this.query,
      categoryId: categoryId ?? this.categoryId,
      location: location ?? this.location,
      minRating: minRating ?? this.minRating,
      maxHourlyRate: maxHourlyRate ?? this.maxHourlyRate,
      isOnline: isOnline ?? this.isOnline,
      sortBy: sortBy ?? this.sortBy,
      page: page ?? this.page,
      limit: limit ?? this.limit,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is MastersSearchRequest &&
        other.query == query &&
        other.categoryId == categoryId &&
        other.location == location &&
        other.minRating == minRating &&
        other.maxHourlyRate == maxHourlyRate &&
        other.isOnline == isOnline &&
        other.sortBy == sortBy &&
        other.page == page &&
        other.limit == limit;
  }

  @override
  int get hashCode {
    return Object.hash(
      query,
      categoryId,
      location,
      minRating,
      maxHourlyRate,
      isOnline,
      sortBy,
      page,
      limit,
    );
  }

  @override
  String toString() {
    return 'MastersSearchRequest(query: $query, categoryId: $categoryId, location: $location, page: $page)';
  }
}
