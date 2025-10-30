import 'dart:async';
import 'package:dartz/dartz.dart';
import '../../models/task_model.dart';
import 'tasks_data_source.dart';

/// Абстрактный репозиторий для задач
abstract class TasksRepository {
  /// Получение списка задач пользователя
  Future<Either<String, List<TaskModel>>> getUserTasks();
  
  /// Получение задачи по ID
  Future<Either<String, TaskModel>> getTaskById(String taskId);
  
  /// Создание новой задачи
  Future<Either<String, TaskModel>> createTask(Map<String, dynamic> taskData);
  
  /// Обновление задачи
  Future<Either<String, TaskModel>> updateTask(String taskId, Map<String, dynamic> taskData);
  
  /// Удаление задачи
  Future<Either<String, bool>> deleteTask(String taskId);
}

/// Реализация репозитория для задач
class TasksRepositoryImpl implements TasksRepository {
  final TasksDataSource _dataSource;
  
  TasksRepositoryImpl({
    required TasksDataSource dataSource,
  }) : _dataSource = dataSource;
  
  @override
  Future<Either<String, List<TaskModel>>> getUserTasks() async {
    try {
      final tasks = await _dataSource.getUserTasks();
      return Right(tasks);
    } catch (e) {
      return Left('Ошибка загрузки задач: ${e.toString()}');
    }
  }
  
  @override
  Future<Either<String, TaskModel>> getTaskById(String taskId) async {
    try {
      final task = await _dataSource.getTaskById(taskId);
      return Right(task);
    } catch (e) {
      return Left('Ошибка загрузки задачи: ${e.toString()}');
    }
  }
  
  @override
  Future<Either<String, TaskModel>> createTask(Map<String, dynamic> taskData) async {
    try {
      final task = await _dataSource.createTask(taskData);
      return Right(task);
    } catch (e) {
      return Left('Ошибка создания задачи: ${e.toString()}');
    }
  }
  
  @override
  Future<Either<String, TaskModel>> updateTask(String taskId, Map<String, dynamic> taskData) async {
    try {
      final task = await _dataSource.updateTask(taskId, taskData);
      return Right(task);
    } catch (e) {
      return Left('Ошибка обновления задачи: ${e.toString()}');
    }
  }
  
  @override
  Future<Either<String, bool>> deleteTask(String taskId) async {
    try {
      final result = await _dataSource.deleteTask(taskId);
      return Right(result);
    } catch (e) {
      return Left('Ошибка удаления задачи: ${e.toString()}');
    }
  }
}
