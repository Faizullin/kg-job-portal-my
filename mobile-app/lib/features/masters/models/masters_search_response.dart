import 'master_model.dart';

/// Ответ на поиск мастеров
class MastersSearchResponse {
  final List<MasterModel> masters;
  final int totalCount;
  final int currentPage;
  final int totalPages;
  final bool hasMore;
  final String? nextPageToken;

  const MastersSearchResponse({
    required this.masters,
    required this.totalCount,
    required this.currentPage,
    required this.totalPages,
    required this.hasMore,
    this.nextPageToken,
  });

  /// Создание из JSON
  factory MastersSearchResponse.fromJson(Map<String, dynamic> json) {
    return MastersSearchResponse(
      masters: (json['masters'] as List)
          .map((master) => MasterModel.fromJson(master as Map<String, dynamic>))
          .toList(),
      totalCount: json['total_count'] as int,
      currentPage: json['current_page'] as int,
      totalPages: json['total_pages'] as int,
      hasMore: json['has_more'] as bool,
      nextPageToken: json['next_page_token'] as String?,
    );
  }

  /// Конвертация в JSON
  Map<String, dynamic> toJson() {
    return {
      'masters': masters.map((master) => master.toJson()).toList(),
      'total_count': totalCount,
      'current_page': currentPage,
      'total_pages': totalPages,
      'has_more': hasMore,
      'next_page_token': nextPageToken,
    };
  }

  /// Создание пустого ответа
  factory MastersSearchResponse.empty() {
    return const MastersSearchResponse(
      masters: [],
      totalCount: 0,
      currentPage: 1,
      totalPages: 0,
      hasMore: false,
    );
  }

  /// Создание ответа с ошибкой
  factory MastersSearchResponse.error(String message) {
    return MastersSearchResponse(
      masters: [],
      totalCount: 0,
      currentPage: 1,
      totalPages: 0,
      hasMore: false,
      nextPageToken: message,
    );
  }

  /// Копирование с изменениями
  MastersSearchResponse copyWith({
    List<MasterModel>? masters,
    int? totalCount,
    int? currentPage,
    int? totalPages,
    bool? hasMore,
    String? nextPageToken,
  }) {
    return MastersSearchResponse(
      masters: masters ?? this.masters,
      totalCount: totalCount ?? this.totalCount,
      currentPage: currentPage ?? this.currentPage,
      totalPages: totalPages ?? this.totalPages,
      hasMore: hasMore ?? this.hasMore,
      nextPageToken: nextPageToken ?? this.nextPageToken,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is MastersSearchResponse &&
        other.totalCount == totalCount &&
        other.currentPage == currentPage &&
        other.totalPages == totalPages &&
        other.hasMore == hasMore;
  }

  @override
  int get hashCode {
    return Object.hash(totalCount, currentPage, totalPages, hasMore);
  }

  @override
  String toString() {
    return 'MastersSearchResponse(totalCount: $totalCount, currentPage: $currentPage, hasMore: $hasMore)';
  }
}
