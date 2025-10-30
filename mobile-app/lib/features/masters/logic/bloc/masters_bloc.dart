import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:dartz/dartz.dart';
import '../data/masters_repository.dart';
import '../../models/service_category_model.dart';
import '../../models/masters_search_request.dart';
import '../../models/masters_search_response.dart';
import 'masters_event.dart';
import 'masters_state.dart';

/// BLoC для управления состоянием мастеров
class MastersBloc extends Bloc<MastersEvent, MastersState> {
  final MastersRepository _repository;

  MastersBloc({
    required MastersRepository repository,
  }) : _repository = repository, super(const MastersInitialState()) {
    
    // Регистрируем обработчики событий
    on<LoadMastersEvent>(_onLoadMasters);
    on<LoadServiceCategoriesEvent>(_onLoadServiceCategories);
    on<LoadMastersStatsEvent>(_onLoadMastersStats);
    on<SearchMastersEvent>(_onSearchMasters);
    on<FilterMastersByCategoryEvent>(_onFilterByCategory);
    on<FilterMastersByLocationEvent>(_onFilterByLocation);
    on<FilterMastersByRatingEvent>(_onFilterByRating);
    on<FilterMastersByOnlineStatusEvent>(_onFilterByOnlineStatus);
    on<SortMastersEvent>(_onSortMasters);
    on<LoadMoreMastersEvent>(_onLoadMoreMasters);
    on<RefreshMastersEvent>(_onRefreshMasters);
    on<ClearFiltersEvent>(_onClearFilters);
    on<ClearSearchEvent>(_onClearSearch);
    on<SelectMasterEvent>(_onSelectMaster);
    on<UpdateSearchFieldEvent>(_onUpdateSearchField);
  }

  /// Загрузка мастеров
  Future<void> _onLoadMasters(
    LoadMastersEvent event,
    Emitter<MastersState> emit,
  ) async {
    emit(const MastersLoadingState());

    // Загружаем все данные параллельно
    final results = await Future.wait([
      _repository.getMasters(event.request),
      _repository.getServiceCategories(),
      _repository.getMastersStats(),
    ]);

    final mastersResult = results[0] as Either<String, MastersSearchResponse>;
    final categoriesResult = results[1] as Either<String, List<ServiceCategoryModel>>;
    final statsResult = results[2] as Either<String, Map<String, dynamic>>;

    // Проверяем результаты
    if (mastersResult.isLeft() || categoriesResult.isLeft() || statsResult.isLeft()) {
      final error = mastersResult.fold(
        (error) => error,
        (_) => categoriesResult.fold(
          (error) => error,
          (_) => statsResult.fold((error) => error, (_) => 'Неизвестная ошибка'),
        ),
      );
      emit(MastersErrorState(error));
      return;
    }

    final masters = mastersResult.getOrElse(() => throw Exception());
    final categories = categoriesResult.getOrElse(() => throw Exception());
    final stats = statsResult.getOrElse(() => throw Exception());

    emit(MastersLoadedState(
      masters: masters.masters,
      categories: categories,
      stats: stats,
      currentRequest: event.request,
      hasMore: masters.hasMore,
      isLoadingMore: false,
    ));
  }

  /// Загрузка категорий услуг
  Future<void> _onLoadServiceCategories(
    LoadServiceCategoriesEvent event,
    Emitter<MastersState> emit,
  ) async {
    final result = await _repository.getServiceCategories();
    
    result.fold(
      (error) => emit(MastersErrorState(error)),
      (categories) {
        if (state is MastersLoadedState) {
          final currentState = state as MastersLoadedState;
          emit(currentState.copyWith(categories: categories));
        }
      },
    );
  }

  /// Загрузка статистики
  Future<void> _onLoadMastersStats(
    LoadMastersStatsEvent event,
    Emitter<MastersState> emit,
  ) async {
    final result = await _repository.getMastersStats();
    
    result.fold(
      (error) => emit(MastersErrorState(error)),
      (stats) {
        if (state is MastersLoadedState) {
          final currentState = state as MastersLoadedState;
          emit(currentState.copyWith(stats: stats));
        }
      },
    );
  }

  /// Поиск мастеров
  Future<void> _onSearchMasters(
    SearchMastersEvent event,
    Emitter<MastersState> emit,
  ) async {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    final newRequest = currentState.currentRequest.copyWith(
      query: event.query.isEmpty ? null : event.query,
      page: 1, // Сбрасываем на первую страницу при поиске
    );

    emit(MastersSearchingState(
      masters: currentState.masters,
      categories: currentState.categories,
      stats: currentState.stats,
      searchQuery: event.query,
      isLoadingMore: false,
    ));

    final result = await _repository.getMasters(newRequest);
    
    result.fold(
      (error) => emit(MastersErrorState(error)),
      (response) {
        if (response.masters.isEmpty) {
          emit(MastersEmptyState(
            categories: currentState.categories,
            stats: currentState.stats,
            searchQuery: event.query,
          ));
        } else {
          emit(MastersLoadedState(
            masters: response.masters,
            categories: currentState.categories,
            stats: currentState.stats,
            currentRequest: newRequest,
            hasMore: response.hasMore,
            isLoadingMore: false,
          ));
        }
      },
    );
  }

  /// Фильтрация по категории
  Future<void> _onFilterByCategory(
    FilterMastersByCategoryEvent event,
    Emitter<MastersState> emit,
  ) async {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    final newRequest = currentState.currentRequest.copyWith(
      categoryId: event.categoryId,
      page: 1,
    );

    emit(MastersFilteringState(
      masters: currentState.masters,
      categories: currentState.categories,
      stats: currentState.stats,
      filters: newRequest,
      isLoadingMore: false,
    ));

    final result = await _repository.getMasters(newRequest);
    
    result.fold(
      (error) => emit(MastersErrorState(error)),
      (response) {
        emit(MastersLoadedState(
          masters: response.masters,
          categories: currentState.categories,
          stats: currentState.stats,
          currentRequest: newRequest,
          hasMore: response.hasMore,
          isLoadingMore: false,
        ));
      },
    );
  }

  /// Фильтрация по локации
  Future<void> _onFilterByLocation(
    FilterMastersByLocationEvent event,
    Emitter<MastersState> emit,
  ) async {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    final newRequest = currentState.currentRequest.copyWith(
      location: event.location,
      page: 1,
    );

    await _loadMastersWithRequest(emit, newRequest, currentState);
  }

  /// Фильтрация по рейтингу
  Future<void> _onFilterByRating(
    FilterMastersByRatingEvent event,
    Emitter<MastersState> emit,
  ) async {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    final newRequest = currentState.currentRequest.copyWith(
      minRating: event.minRating,
      page: 1,
    );

    await _loadMastersWithRequest(emit, newRequest, currentState);
  }

  /// Фильтрация по онлайн статусу
  Future<void> _onFilterByOnlineStatus(
    FilterMastersByOnlineStatusEvent event,
    Emitter<MastersState> emit,
  ) async {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    final newRequest = currentState.currentRequest.copyWith(
      isOnline: event.isOnline,
      page: 1,
    );

    await _loadMastersWithRequest(emit, newRequest, currentState);
  }

  /// Сортировка мастеров
  Future<void> _onSortMasters(
    SortMastersEvent event,
    Emitter<MastersState> emit,
  ) async {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    final newRequest = currentState.currentRequest.copyWith(
      sortBy: event.sortBy,
      page: 1,
    );

    await _loadMastersWithRequest(emit, newRequest, currentState);
  }

  /// Загрузка дополнительных мастеров
  Future<void> _onLoadMoreMasters(
    LoadMoreMastersEvent event,
    Emitter<MastersState> emit,
  ) async {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    if (!currentState.hasMore || currentState.isLoadingMore) return;

    emit(currentState.copyWith(isLoadingMore: true));

    final newRequest = currentState.currentRequest.copyWith(
      page: currentState.currentRequest.page + 1,
    );

    final result = await _repository.getMasters(newRequest);
    
    result.fold(
      (error) => emit(MastersErrorState(error)),
      (response) {
        final allMasters = [...currentState.masters, ...response.masters];
        emit(currentState.copyWith(
          masters: allMasters,
          currentRequest: newRequest,
          hasMore: response.hasMore,
          isLoadingMore: false,
        ));
      },
    );
  }

  /// Обновление данных
  Future<void> _onRefreshMasters(
    RefreshMastersEvent event,
    Emitter<MastersState> emit,
  ) async {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    final newRequest = currentState.currentRequest.copyWith(page: 1);

    await _loadMastersWithRequest(emit, newRequest, currentState);
  }

  /// Очистка фильтров
  void _onClearFilters(
    ClearFiltersEvent event,
    Emitter<MastersState> emit,
  ) {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    final newRequest = MastersSearchRequest(
      query: currentState.currentRequest.query,
      page: 1,
    );

    add(LoadMastersEvent(newRequest));
  }

  /// Очистка поиска
  void _onClearSearch(
    ClearSearchEvent event,
    Emitter<MastersState> emit,
  ) {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    final newRequest = currentState.currentRequest.copyWith(
      query: null,
      page: 1,
    );

    add(LoadMastersEvent(newRequest));
  }

  /// Выбор мастера
  void _onSelectMaster(
    SelectMasterEvent event,
    Emitter<MastersState> emit,
  ) {
    if (state is! MastersLoadedState) return;

    final currentState = state as MastersLoadedState;
    final selectedMaster = currentState.masters.firstWhere(
      (master) => master.id == event.masterId,
      orElse: () => throw Exception('Мастер не найден'),
    );

    emit(MasterSelectedState(
      selectedMaster: selectedMaster,
      masters: currentState.masters,
      categories: currentState.categories,
      stats: currentState.stats,
    ));
  }

  /// Обновление полей поиска
  void _onUpdateSearchField(
    UpdateSearchFieldEvent event,
    Emitter<MastersState> emit,
  ) {
    // Это событие можно использовать для обновления полей формы поиска
    // Пока не реализовано, так как нет формы поиска в UI
  }

  /// Вспомогательный метод для загрузки мастеров с запросом
  Future<void> _loadMastersWithRequest(
    Emitter<MastersState> emit,
    MastersSearchRequest request,
    MastersLoadedState currentState,
  ) async {
    final result = await _repository.getMasters(request);
    
    result.fold(
      (error) => emit(MastersErrorState(error)),
      (response) {
        emit(MastersLoadedState(
          masters: response.masters,
          categories: currentState.categories,
          stats: currentState.stats,
          currentRequest: request,
          hasMore: response.hasMore,
          isLoadingMore: false,
        ));
      },
    );
  }
}
