import 'package:flutter_bloc/flutter_bloc.dart';
import '../data/home_repository.dart';
import 'home_event.dart';
import 'home_state.dart';

/// BLoC для управления состоянием home экрана
class HomeBloc extends Bloc<HomeEvent, HomeState> {
  final HomeRepository _repository;
  
  HomeBloc({
    required HomeRepository repository,
  }) : _repository = repository, super(HomeInitialState()) {
    on<LoadHomeDataEvent>(_onLoadHomeData);
    on<SearchEvent>(_onSearch);
    on<RefreshHomeDataEvent>(_onRefresh);
  }
  
  void _onLoadHomeData(LoadHomeDataEvent event, Emitter<HomeState> emit) async {
    emit(HomeLoadingState());
    
    try {
      // Здесь будет логика загрузки данных
      await Future.delayed(Duration(seconds: 1)); // Имитация загрузки
      emit(HomeLoadedState());
    } catch (e) {
      emit(HomeErrorState('Ошибка загрузки данных: ${e.toString()}'));
    }
  }
  
  void _onSearch(SearchEvent event, Emitter<HomeState> emit) async {
    if (state is HomeLoadedState) {
      emit((state as HomeLoadedState).copyWith(searchQuery: event.query));
    }
  }
  
  void _onRefresh(RefreshHomeDataEvent event, Emitter<HomeState> emit) async {
    if (state is HomeLoadedState) {
      emit((state as HomeLoadedState).copyWith(isRefreshing: true));
      
      try {
        // Здесь будет логика обновления данных
        await Future.delayed(Duration(seconds: 1)); // Имитация обновления
        emit((state as HomeLoadedState).copyWith(isRefreshing: false));
      } catch (e) {
        emit(HomeErrorState('Ошибка обновления данных: ${e.toString()}'));
      }
    }
  }
}
