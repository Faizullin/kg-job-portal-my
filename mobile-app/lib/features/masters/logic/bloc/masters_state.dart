import 'package:equatable/equatable.dart';
import '../../models/master_model.dart';
import '../../models/service_category_model.dart';
import '../../models/masters_search_request.dart';

/// Состояния для MastersBloc
abstract class MastersState extends Equatable {
  const MastersState();

  @override
  List<Object?> get props => [];
}

/// Начальное состояние
class MastersInitialState extends MastersState {
  const MastersInitialState();
}

/// Загрузка данных
class MastersLoadingState extends MastersState {
  const MastersLoadingState();
}

/// Мастера успешно загружены
class MastersLoadedState extends MastersState {
  final List<MasterModel> masters;
  final List<ServiceCategoryModel> categories;
  final Map<String, dynamic> stats;
  final MastersSearchRequest currentRequest;
  final bool hasMore;
  final bool isLoadingMore;

  const MastersLoadedState({
    required this.masters,
    required this.categories,
    required this.stats,
    required this.currentRequest,
    required this.hasMore,
    required this.isLoadingMore,
  });

  @override
  List<Object?> get props => [
        masters,
        categories,
        stats,
        currentRequest,
        hasMore,
        isLoadingMore,
      ];

  MastersLoadedState copyWith({
    List<MasterModel>? masters,
    List<ServiceCategoryModel>? categories,
    Map<String, dynamic>? stats,
    MastersSearchRequest? currentRequest,
    bool? hasMore,
    bool? isLoadingMore,
  }) {
    return MastersLoadedState(
      masters: masters ?? this.masters,
      categories: categories ?? this.categories,
      stats: stats ?? this.stats,
      currentRequest: currentRequest ?? this.currentRequest,
      hasMore: hasMore ?? this.hasMore,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
    );
  }
}

/// Ошибка загрузки мастеров
class MastersErrorState extends MastersState {
  final String message;

  const MastersErrorState(this.message);

  @override
  List<Object?> get props => [message];
}

/// Поиск мастеров
class MastersSearchingState extends MastersState {
  final List<MasterModel> masters;
  final List<ServiceCategoryModel> categories;
  final Map<String, dynamic> stats;
  final String searchQuery;
  final bool isLoadingMore;

  const MastersSearchingState({
    required this.masters,
    required this.categories,
    required this.stats,
    required this.searchQuery,
    required this.isLoadingMore,
  });

  @override
  List<Object?> get props => [
        masters,
        categories,
        stats,
        searchQuery,
        isLoadingMore,
      ];
}

/// Фильтрация мастеров
class MastersFilteringState extends MastersState {
  final List<MasterModel> masters;
  final List<ServiceCategoryModel> categories;
  final Map<String, dynamic> stats;
  final MastersSearchRequest filters;
  final bool isLoadingMore;

  const MastersFilteringState({
    required this.masters,
    required this.categories,
    required this.stats,
    required this.filters,
    required this.isLoadingMore,
  });

  @override
  List<Object?> get props => [
        masters,
        categories,
        stats,
        filters,
        isLoadingMore,
      ];
}

/// Загрузка дополнительных мастеров
class MastersLoadingMoreState extends MastersState {
  final List<MasterModel> masters;
  final List<ServiceCategoryModel> categories;
  final Map<String, dynamic> stats;
  final MastersSearchRequest currentRequest;

  const MastersLoadingMoreState({
    required this.masters,
    required this.categories,
    required this.stats,
    required this.currentRequest,
  });

  @override
  List<Object?> get props => [
        masters,
        categories,
        stats,
        currentRequest,
      ];
}

/// Мастер выбран
class MasterSelectedState extends MastersState {
  final MasterModel selectedMaster;
  final List<MasterModel> masters;
  final List<ServiceCategoryModel> categories;
  final Map<String, dynamic> stats;

  const MasterSelectedState({
    required this.selectedMaster,
    required this.masters,
    required this.categories,
    required this.stats,
  });

  @override
  List<Object?> get props => [
        selectedMaster,
        masters,
        categories,
        stats,
      ];
}

/// Пустой результат поиска
class MastersEmptyState extends MastersState {
  final List<ServiceCategoryModel> categories;
  final Map<String, dynamic> stats;
  final String searchQuery;

  const MastersEmptyState({
    required this.categories,
    required this.stats,
    required this.searchQuery,
  });

  @override
  List<Object?> get props => [categories, stats, searchQuery];
}
