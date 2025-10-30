import 'package:equatable/equatable.dart';
import '../../models/masters_search_request.dart';

/// События для MastersBloc
abstract class MastersEvent extends Equatable {
  const MastersEvent();

  @override
  List<Object?> get props => [];
}

/// Загрузка мастеров
class LoadMastersEvent extends MastersEvent {
  final MastersSearchRequest request;

  const LoadMastersEvent(this.request);

  @override
  List<Object?> get props => [request];
}

/// Загрузка категорий услуг
class LoadServiceCategoriesEvent extends MastersEvent {
  const LoadServiceCategoriesEvent();
}

/// Загрузка статистики мастеров
class LoadMastersStatsEvent extends MastersEvent {
  const LoadMastersStatsEvent();
}

/// Поиск мастеров
class SearchMastersEvent extends MastersEvent {
  final String query;

  const SearchMastersEvent(this.query);

  @override
  List<Object?> get props => [query];
}

/// Фильтрация мастеров по категории
class FilterMastersByCategoryEvent extends MastersEvent {
  final String categoryId;

  const FilterMastersByCategoryEvent(this.categoryId);

  @override
  List<Object?> get props => [categoryId];
}

/// Фильтрация мастеров по локации
class FilterMastersByLocationEvent extends MastersEvent {
  final String location;

  const FilterMastersByLocationEvent(this.location);

  @override
  List<Object?> get props => [location];
}

/// Фильтрация мастеров по рейтингу
class FilterMastersByRatingEvent extends MastersEvent {
  final double minRating;

  const FilterMastersByRatingEvent(this.minRating);

  @override
  List<Object?> get props => [minRating];
}

/// Фильтрация мастеров по онлайн статусу
class FilterMastersByOnlineStatusEvent extends MastersEvent {
  final bool isOnline;

  const FilterMastersByOnlineStatusEvent(this.isOnline);

  @override
  List<Object?> get props => [isOnline];
}

/// Сортировка мастеров
class SortMastersEvent extends MastersEvent {
  final String sortBy; // 'rating', 'price', 'distance'

  const SortMastersEvent(this.sortBy);

  @override
  List<Object?> get props => [sortBy];
}

/// Загрузка следующей страницы
class LoadMoreMastersEvent extends MastersEvent {
  const LoadMoreMastersEvent();
}

/// Обновление данных
class RefreshMastersEvent extends MastersEvent {
  const RefreshMastersEvent();
}

/// Очистка фильтров
class ClearFiltersEvent extends MastersEvent {
  const ClearFiltersEvent();
}

/// Сброс поиска
class ClearSearchEvent extends MastersEvent {
  const ClearSearchEvent();
}

/// Выбор мастера
class SelectMasterEvent extends MastersEvent {
  final String masterId;

  const SelectMasterEvent(this.masterId);

  @override
  List<Object?> get props => [masterId];
}

/// Обновление полей поиска
class UpdateSearchFieldEvent extends MastersEvent {
  final String field;
  final String value;

  const UpdateSearchFieldEvent(this.field, this.value);

  @override
  List<Object?> get props => [field, value];
}
