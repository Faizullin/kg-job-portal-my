import 'package:equatable/equatable.dart';

/// События для TasksBloc
abstract class TasksEvent extends Equatable {
  const TasksEvent();

  @override
  List<Object?> get props => [];
}

/// Загрузка задач пользователя
class LoadUserTasksEvent extends TasksEvent {
  const LoadUserTasksEvent();
}

/// Обновление списка задач
class RefreshTasksEvent extends TasksEvent {
  const RefreshTasksEvent();
}

/// Фильтрация задач по статусу
class FilterTasksByStatusEvent extends TasksEvent {
  final String status;

  const FilterTasksByStatusEvent(this.status);

  @override
  List<Object?> get props => [status];
}

/// Фильтрация задач по категории
class FilterTasksByCategoryEvent extends TasksEvent {
  final String category;

  const FilterTasksByCategoryEvent(this.category);

  @override
  List<Object?> get props => [category];
}

/// Сортировка задач
class SortTasksEvent extends TasksEvent {
  final String sortBy; // 'date', 'priority', 'status', 'price'

  const SortTasksEvent(this.sortBy);

  @override
  List<Object?> get props => [sortBy];
}

/// Выбор задачи
class SelectTaskEvent extends TasksEvent {
  final String taskId;

  const SelectTaskEvent(this.taskId);

  @override
  List<Object?> get props => [taskId];
}

/// Создание новой задачи
class CreateTaskEvent extends TasksEvent {
  final Map<String, dynamic> taskData;

  const CreateTaskEvent(this.taskData);

  @override
  List<Object?> get props => [taskData];
}

/// Обновление задачи
class UpdateTaskEvent extends TasksEvent {
  final String taskId;
  final Map<String, dynamic> taskData;

  const UpdateTaskEvent(this.taskId, this.taskData);

  @override
  List<Object?> get props => [taskId, taskData];
}

/// Удаление задачи
class DeleteTaskEvent extends TasksEvent {
  final String taskId;

  const DeleteTaskEvent(this.taskId);

  @override
  List<Object?> get props => [taskId];
}

/// Очистка фильтров
class ClearFiltersEvent extends TasksEvent {
  const ClearFiltersEvent();
}

/// Поиск задач
class SearchTasksEvent extends TasksEvent {
  final String query;

  const SearchTasksEvent(this.query);

  @override
  List<Object?> get props => [query];
}

/// Очистка поиска
class ClearSearchEvent extends TasksEvent {
  const ClearSearchEvent();
}
