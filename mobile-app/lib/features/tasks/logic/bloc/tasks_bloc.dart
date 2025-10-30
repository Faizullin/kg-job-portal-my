import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:dartz/dartz.dart';
import '../data/tasks_repository.dart';
import '../../models/task_model.dart';
import 'tasks_event.dart';
import 'tasks_state.dart';

/// BLoC для управления состоянием задач
class TasksBloc extends Bloc<TasksEvent, TasksState> {
  final TasksRepository _repository;

  TasksBloc({
    required TasksRepository repository,
  }) : _repository = repository, super(const TasksInitialState()) {
    
    // Регистрируем обработчики событий
    on<LoadUserTasksEvent>(_onLoadUserTasks);
    on<RefreshTasksEvent>(_onRefreshTasks);
    on<FilterTasksByStatusEvent>(_onFilterByStatus);
    on<FilterTasksByCategoryEvent>(_onFilterByCategory);
    on<SortTasksEvent>(_onSortTasks);
    on<SelectTaskEvent>(_onSelectTask);
    on<CreateTaskEvent>(_onCreateTask);
    on<UpdateTaskEvent>(_onUpdateTask);
    on<DeleteTaskEvent>(_onDeleteTask);
    on<ClearFiltersEvent>(_onClearFilters);
    on<SearchTasksEvent>(_onSearchTasks);
    on<ClearSearchEvent>(_onClearSearch);
  }

  /// Загрузка задач пользователя
  Future<void> _onLoadUserTasks(
    LoadUserTasksEvent event,
    Emitter<TasksState> emit,
  ) async {
    emit(const TasksLoadingState());

    final result = await _repository.getUserTasks();
    
    result.fold(
      (error) => emit(TasksErrorState(error)),
      (tasks) {
        if (tasks.isEmpty) {
          emit(const TasksEmptyState('У вас пока нет задач'));
        } else {
          emit(TasksLoadedState(
            tasks: tasks,
            filteredTasks: tasks,
          ));
        }
      },
    );
  }

  /// Обновление задач
  Future<void> _onRefreshTasks(
    RefreshTasksEvent event,
    Emitter<TasksState> emit,
  ) async {
    if (state is TasksLoadedState) {
      final currentState = state as TasksLoadedState;
      emit(TasksLoadedState(
        tasks: currentState.tasks,
        filteredTasks: currentState.filteredTasks,
        currentFilter: currentState.currentFilter,
        currentSortBy: currentState.currentSortBy,
        searchQuery: currentState.searchQuery,
      ));
    }

    final result = await _repository.getUserTasks();
    
    result.fold(
      (error) => emit(TasksErrorState(error)),
      (tasks) {
        if (state is TasksLoadedState) {
          final currentState = state as TasksLoadedState;
          final filteredTasks = _applyFiltersAndSort(
            tasks,
            currentState.currentFilter,
            currentState.currentSortBy,
            currentState.searchQuery,
          );
          
          emit(TasksLoadedState(
            tasks: tasks,
            filteredTasks: filteredTasks,
            currentFilter: currentState.currentFilter,
            currentSortBy: currentState.currentSortBy,
            searchQuery: currentState.searchQuery,
          ));
        } else {
          emit(TasksLoadedState(
            tasks: tasks,
            filteredTasks: tasks,
          ));
        }
      },
    );
  }

  /// Фильтрация по статусу
  void _onFilterByStatus(
    FilterTasksByStatusEvent event,
    Emitter<TasksState> emit,
  ) {
    if (state is! TasksLoadedState) return;

    final currentState = state as TasksLoadedState;
    final filteredTasks = _applyFiltersAndSort(
      currentState.tasks,
      event.status,
      currentState.currentSortBy,
      currentState.searchQuery,
    );

    emit(currentState.copyWith(
      filteredTasks: filteredTasks,
      currentFilter: event.status,
    ));
  }

  /// Фильтрация по категории
  void _onFilterByCategory(
    FilterTasksByCategoryEvent event,
    Emitter<TasksState> emit,
  ) {
    if (state is! TasksLoadedState) return;

    final currentState = state as TasksLoadedState;
    final filteredTasks = _applyFiltersAndSort(
      currentState.tasks,
      currentState.currentFilter,
      currentState.currentSortBy,
      currentState.searchQuery,
      category: event.category,
    );

    emit(currentState.copyWith(
      filteredTasks: filteredTasks,
    ));
  }

  /// Сортировка задач
  void _onSortTasks(
    SortTasksEvent event,
    Emitter<TasksState> emit,
  ) {
    if (state is! TasksLoadedState) return;

    final currentState = state as TasksLoadedState;
    final filteredTasks = _applyFiltersAndSort(
      currentState.tasks,
      currentState.currentFilter,
      event.sortBy,
      currentState.searchQuery,
    );

    emit(currentState.copyWith(
      filteredTasks: filteredTasks,
      currentSortBy: event.sortBy,
    ));
  }

  /// Выбор задачи
  void _onSelectTask(
    SelectTaskEvent event,
    Emitter<TasksState> emit,
  ) {
    if (state is! TasksLoadedState) return;

    final currentState = state as TasksLoadedState;
    final selectedTask = currentState.tasks.firstWhere(
      (task) => task.id == event.taskId,
      orElse: () => throw Exception('Задача не найдена'),
    );

    emit(TaskSelectedState(selectedTask, currentState.tasks));
  }

  /// Создание задачи
  Future<void> _onCreateTask(
    CreateTaskEvent event,
    Emitter<TasksState> emit,
  ) async {
    if (state is! TasksLoadedState) return;

    final currentState = state as TasksLoadedState;
    emit(TasksCreatingState(currentState.tasks));

    final result = await _repository.createTask(event.taskData);
    
    result.fold(
      (error) => emit(TasksCreateErrorState(currentState.tasks, error)),
      (newTask) {
        final updatedTasks = [...currentState.tasks, newTask];
        final filteredTasks = _applyFiltersAndSort(
          updatedTasks,
          currentState.currentFilter,
          currentState.currentSortBy,
          currentState.searchQuery,
        );
        
        emit(TasksCreatedState(updatedTasks, newTask));
        emit(TasksLoadedState(
          tasks: updatedTasks,
          filteredTasks: filteredTasks,
          currentFilter: currentState.currentFilter,
          currentSortBy: currentState.currentSortBy,
          searchQuery: currentState.searchQuery,
        ));
      },
    );
  }

  /// Обновление задачи
  Future<void> _onUpdateTask(
    UpdateTaskEvent event,
    Emitter<TasksState> emit,
  ) async {
    if (state is! TasksLoadedState) return;

    final currentState = state as TasksLoadedState;
    emit(TasksUpdatingState(currentState.tasks));

    final result = await _repository.updateTask(event.taskId, event.taskData);
    
    result.fold(
      (error) => emit(TasksUpdateErrorState(currentState.tasks, error)),
      (updatedTask) {
        final updatedTasks = currentState.tasks.map((task) {
          return task.id == event.taskId ? updatedTask : task;
        }).toList();
        
        final filteredTasks = _applyFiltersAndSort(
          updatedTasks,
          currentState.currentFilter,
          currentState.currentSortBy,
          currentState.searchQuery,
        );
        
        emit(TasksUpdatedState(updatedTasks, updatedTask));
        emit(TasksLoadedState(
          tasks: updatedTasks,
          filteredTasks: filteredTasks,
          currentFilter: currentState.currentFilter,
          currentSortBy: currentState.currentSortBy,
          searchQuery: currentState.searchQuery,
        ));
      },
    );
  }

  /// Удаление задачи
  Future<void> _onDeleteTask(
    DeleteTaskEvent event,
    Emitter<TasksState> emit,
  ) async {
    if (state is! TasksLoadedState) return;

    final currentState = state as TasksLoadedState;
    emit(TasksDeletingState(currentState.tasks));

    final result = await _repository.deleteTask(event.taskId);
    
    result.fold(
      (error) => emit(TasksDeleteErrorState(currentState.tasks, error)),
      (success) {
        final updatedTasks = currentState.tasks
            .where((task) => task.id != event.taskId)
            .toList();
        
        final filteredTasks = _applyFiltersAndSort(
          updatedTasks,
          currentState.currentFilter,
          currentState.currentSortBy,
          currentState.searchQuery,
        );
        
        emit(TasksDeletedState(updatedTasks, event.taskId));
        emit(TasksLoadedState(
          tasks: updatedTasks,
          filteredTasks: filteredTasks,
          currentFilter: currentState.currentFilter,
          currentSortBy: currentState.currentSortBy,
          searchQuery: currentState.searchQuery,
        ));
      },
    );
  }

  /// Очистка фильтров
  void _onClearFilters(
    ClearFiltersEvent event,
    Emitter<TasksState> emit,
  ) {
    if (state is! TasksLoadedState) return;

    final currentState = state as TasksLoadedState;
    final filteredTasks = _applyFiltersAndSort(
      currentState.tasks,
      null,
      currentState.currentSortBy,
      currentState.searchQuery,
    );

    emit(currentState.copyWith(
      filteredTasks: filteredTasks,
      currentFilter: null,
    ));
  }

  /// Поиск задач
  void _onSearchTasks(
    SearchTasksEvent event,
    Emitter<TasksState> emit,
  ) {
    if (state is! TasksLoadedState) return;

    final currentState = state as TasksLoadedState;
    final filteredTasks = _applyFiltersAndSort(
      currentState.tasks,
      currentState.currentFilter,
      currentState.currentSortBy,
      event.query.isEmpty ? null : event.query,
    );

    emit(currentState.copyWith(
      filteredTasks: filteredTasks,
      searchQuery: event.query.isEmpty ? null : event.query,
    ));
  }

  /// Очистка поиска
  void _onClearSearch(
    ClearSearchEvent event,
    Emitter<TasksState> emit,
  ) {
    if (state is! TasksLoadedState) return;

    final currentState = state as TasksLoadedState;
    final filteredTasks = _applyFiltersAndSort(
      currentState.tasks,
      currentState.currentFilter,
      currentState.currentSortBy,
      null,
    );

    emit(currentState.copyWith(
      filteredTasks: filteredTasks,
      searchQuery: null,
    ));
  }

  /// Применение фильтров и сортировки
  List<TaskModel> _applyFiltersAndSort(
    List<TaskModel> tasks,
    String? statusFilter,
    String? sortBy,
    String? searchQuery, {
    String? category,
  }) {
    var filteredTasks = tasks;

    // Фильтрация по статусу
    if (statusFilter != null && statusFilter.isNotEmpty) {
      filteredTasks = filteredTasks
          .where((task) => task.status == statusFilter)
          .toList();
    }

    // Фильтрация по категории
    if (category != null && category.isNotEmpty) {
      filteredTasks = filteredTasks
          .where((task) => task.category == category)
          .toList();
    }

    // Поиск по тексту
    if (searchQuery != null && searchQuery.isNotEmpty) {
      final query = searchQuery.toLowerCase();
      filteredTasks = filteredTasks
          .where((task) =>
              task.title.toLowerCase().contains(query) ||
              task.description.toLowerCase().contains(query) ||
              task.location.toLowerCase().contains(query))
          .toList();
    }

    // Сортировка
    switch (sortBy) {
      case 'date':
        filteredTasks.sort((a, b) => b.createdAt.compareTo(a.createdAt));
        break;
      case 'priority':
        final priorityOrder = {'high': 3, 'medium': 2, 'low': 1};
        filteredTasks.sort((a, b) =>
            (priorityOrder[b.priority] ?? 0).compareTo(priorityOrder[a.priority] ?? 0));
        break;
      case 'status':
        filteredTasks.sort((a, b) => a.status.compareTo(b.status));
        break;
      case 'price':
        filteredTasks.sort((a, b) {
          final aPrice = a.estimatedPrice ?? 0;
          final bPrice = b.estimatedPrice ?? 0;
          return bPrice.compareTo(aPrice);
        });
        break;
      default:
        // По умолчанию сортируем по дате создания
        filteredTasks.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    }

    return filteredTasks;
  }
}
