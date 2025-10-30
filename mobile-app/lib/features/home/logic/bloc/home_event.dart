/// События для home BLoC
abstract class HomeEvent {}

/// Событие загрузки данных
class LoadHomeDataEvent extends HomeEvent {}

/// Событие поиска
class SearchEvent extends HomeEvent {
  final String query;
  
  SearchEvent(this.query);
}

/// Событие обновления данных
class RefreshHomeDataEvent extends HomeEvent {}
