/// Состояния для home BLoC
abstract class HomeState {}

/// Начальное состояние
class HomeInitialState extends HomeState {}

/// Состояние загрузки
class HomeLoadingState extends HomeState {}

/// Состояние успешной загрузки
class HomeLoadedState extends HomeState {
  final String searchQuery;
  final bool isRefreshing;
  
  HomeLoadedState({
    this.searchQuery = '',
    this.isRefreshing = false,
  });
  
  HomeLoadedState copyWith({
    String? searchQuery,
    bool? isRefreshing,
  }) {
    return HomeLoadedState(
      searchQuery: searchQuery ?? this.searchQuery,
      isRefreshing: isRefreshing ?? this.isRefreshing,
    );
  }
}

/// Состояние ошибки
class HomeErrorState extends HomeState {
  final String message;
  
  HomeErrorState(this.message);
}
