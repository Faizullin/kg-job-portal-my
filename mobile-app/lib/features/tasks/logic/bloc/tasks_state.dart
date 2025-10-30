import 'package:equatable/equatable.dart';
import '../../models/task_model.dart';

/// Состояния для TasksBloc
abstract class TasksState extends Equatable {
  const TasksState();

  @override
  List<Object?> get props => [];
}

/// Начальное состояние
class TasksInitialState extends TasksState {
  const TasksInitialState();
}

/// Загрузка задач
class TasksLoadingState extends TasksState {
  const TasksLoadingState();
}

/// Задачи успешно загружены
class TasksLoadedState extends TasksState {
  final List<TaskModel> tasks;
  final List<TaskModel> filteredTasks;
  final String? currentFilter;
  final String? currentSortBy;
  final String? searchQuery;

  const TasksLoadedState({
    required this.tasks,
    required this.filteredTasks,
    this.currentFilter,
    this.currentSortBy,
    this.searchQuery,
  });

  @override
  List<Object?> get props => [
        tasks,
        filteredTasks,
        currentFilter,
        currentSortBy,
        searchQuery,
      ];

  TasksLoadedState copyWith({
    List<TaskModel>? tasks,
    List<TaskModel>? filteredTasks,
    String? currentFilter,
    String? currentSortBy,
    String? searchQuery,
  }) {
    return TasksLoadedState(
      tasks: tasks ?? this.tasks,
      filteredTasks: filteredTasks ?? this.filteredTasks,
      currentFilter: currentFilter ?? this.currentFilter,
      currentSortBy: currentSortBy ?? this.currentSortBy,
      searchQuery: searchQuery ?? this.searchQuery,
    );
  }
}

/// Ошибка загрузки задач
class TasksErrorState extends TasksState {
  final String message;

  const TasksErrorState(this.message);

  @override
  List<Object?> get props => [message];
}

/// Создание задачи
class TasksCreatingState extends TasksState {
  final List<TaskModel> tasks;

  const TasksCreatingState(this.tasks);

  @override
  List<Object?> get props => [tasks];
}

/// Задача успешно создана
class TasksCreatedState extends TasksState {
  final List<TaskModel> tasks;
  final TaskModel newTask;

  const TasksCreatedState(this.tasks, this.newTask);

  @override
  List<Object?> get props => [tasks, newTask];
}

/// Ошибка создания задачи
class TasksCreateErrorState extends TasksState {
  final List<TaskModel> tasks;
  final String message;

  const TasksCreateErrorState(this.tasks, this.message);

  @override
  List<Object?> get props => [tasks, message];
}

/// Обновление задачи
class TasksUpdatingState extends TasksState {
  final List<TaskModel> tasks;

  const TasksUpdatingState(this.tasks);

  @override
  List<Object?> get props => [tasks];
}

/// Задача успешно обновлена
class TasksUpdatedState extends TasksState {
  final List<TaskModel> tasks;
  final TaskModel updatedTask;

  const TasksUpdatedState(this.tasks, this.updatedTask);

  @override
  List<Object?> get props => [tasks, updatedTask];
}

/// Ошибка обновления задачи
class TasksUpdateErrorState extends TasksState {
  final List<TaskModel> tasks;
  final String message;

  const TasksUpdateErrorState(this.tasks, this.message);

  @override
  List<Object?> get props => [tasks, message];
}

/// Удаление задачи
class TasksDeletingState extends TasksState {
  final List<TaskModel> tasks;

  const TasksDeletingState(this.tasks);

  @override
  List<Object?> get props => [tasks];
}

/// Задача успешно удалена
class TasksDeletedState extends TasksState {
  final List<TaskModel> tasks;
  final String deletedTaskId;

  const TasksDeletedState(this.tasks, this.deletedTaskId);

  @override
  List<Object?> get props => [tasks, deletedTaskId];
}

/// Ошибка удаления задачи
class TasksDeleteErrorState extends TasksState {
  final List<TaskModel> tasks;
  final String message;

  const TasksDeleteErrorState(this.tasks, this.message);

  @override
  List<Object?> get props => [tasks, message];
}

/// Задача выбрана
class TaskSelectedState extends TasksState {
  final TaskModel selectedTask;
  final List<TaskModel> tasks;

  const TaskSelectedState(this.selectedTask, this.tasks);

  @override
  List<Object?> get props => [selectedTask, tasks];
}

/// Пустой результат
class TasksEmptyState extends TasksState {
  final String message;

  const TasksEmptyState(this.message);

  @override
  List<Object?> get props => [message];
}
