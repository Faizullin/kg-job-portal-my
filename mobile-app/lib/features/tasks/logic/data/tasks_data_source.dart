import 'dart:async';
import '../../models/task_model.dart';

/// Абстрактный источник данных для задач
abstract class TasksDataSource {
  /// Получение списка задач пользователя
  Future<List<TaskModel>> getUserTasks();
  
  /// Получение задачи по ID
  Future<TaskModel> getTaskById(String taskId);
  
  /// Создание новой задачи
  Future<TaskModel> createTask(Map<String, dynamic> taskData);
  
  /// Обновление задачи
  Future<TaskModel> updateTask(String taskId, Map<String, dynamic> taskData);
  
  /// Удаление задачи
  Future<bool> deleteTask(String taskId);
}

/// Реализация источника данных для задач
class TasksDataSourceImpl implements TasksDataSource {
  
  @override
  Future<List<TaskModel>> getUserTasks() async {
    // Имитация загрузки данных
    await Future.delayed(Duration(milliseconds: 800));
    
    // Возвращаем тестовые данные
    return [
      TaskModel(
        id: '1',
        title: 'Ремонт сантехники',
        description: 'Нужно починить кран в ванной комнате',
        status: 'completed',
        priority: 'high',
        masterId: 'master_1',
        masterName: 'Алексей Петров',
        clientId: 'client_1',
        clientName: 'Умар Исмаилов',
        location: 'Бишкек, ул. Чуй, 123',
        category: 'Сантехника',
        estimatedPrice: 5000.0,
        finalPrice: 4500.0,
        createdAt: DateTime.now().subtract(Duration(days: 5)),
        updatedAt: DateTime.now().subtract(Duration(days: 1)),
        scheduledDate: DateTime.now().subtract(Duration(days: 2)),
        completedDate: DateTime.now().subtract(Duration(days: 1)),
      ),
      TaskModel(
        id: '2',
        title: 'Установка розетки',
        description: 'Установить новую розетку в спальне',
        status: 'in_progress',
        priority: 'medium',
        masterId: 'master_2',
        masterName: 'Дмитрий Иванов',
        clientId: 'client_1',
        clientName: 'Умар Исмаилов',
        location: 'Бишкек, ул. Советская, 45',
        category: 'Электрика',
        estimatedPrice: 2500.0,
        finalPrice: null,
        createdAt: DateTime.now().subtract(Duration(days: 3)),
        updatedAt: DateTime.now().subtract(Duration(hours: 2)),
        scheduledDate: DateTime.now().add(Duration(days: 1)),
        completedDate: null,
      ),
      TaskModel(
        id: '3',
        title: 'Сборка мебели',
        description: 'Собрать шкаф из ИКЕА',
        status: 'pending',
        priority: 'low',
        masterId: null,
        masterName: null,
        clientId: 'client_1',
        clientName: 'Умар Исмаилов',
        location: 'Бишкек, ул. Ленина, 78',
        category: 'Мебель',
        estimatedPrice: 8000.0,
        finalPrice: null,
        createdAt: DateTime.now().subtract(Duration(days: 1)),
        updatedAt: DateTime.now().subtract(Duration(days: 1)),
        scheduledDate: DateTime.now().add(Duration(days: 3)),
        completedDate: null,
      ),
      TaskModel(
        id: '4',
        title: 'Уборка квартиры',
        description: 'Генеральная уборка 3-комнатной квартиры',
        status: 'cancelled',
        priority: 'low',
        masterId: 'master_3',
        masterName: 'Анна Смирнова',
        clientId: 'client_1',
        clientName: 'Умар Исмаилов',
        location: 'Бишкек, ул. Манаса, 12',
        category: 'Уборка',
        estimatedPrice: 6000.0,
        finalPrice: null,
        createdAt: DateTime.now().subtract(Duration(days: 7)),
        updatedAt: DateTime.now().subtract(Duration(days: 4)),
        scheduledDate: DateTime.now().subtract(Duration(days: 4)),
        completedDate: null,
      ),
    ];
  }
  
  @override
  Future<TaskModel> getTaskById(String taskId) async {
    // Имитация загрузки
    await Future.delayed(Duration(milliseconds: 600));
    
    // Возвращаем тестовую задачу
    return TaskModel(
      id: taskId,
      title: 'Детали задачи',
      description: 'Подробное описание задачи',
      status: 'pending',
      priority: 'medium',
      location: 'Бишкек',
      category: 'Общие работы',
      createdAt: DateTime.now().subtract(Duration(days: 1)),
      updatedAt: DateTime.now(),
    );
  }
  
  @override
  Future<TaskModel> createTask(Map<String, dynamic> taskData) async {
    // Имитация создания
    await Future.delayed(Duration(milliseconds: 1000));
    
    return TaskModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: taskData['title'] as String,
      description: taskData['description'] as String,
      status: 'pending',
      priority: taskData['priority'] as String? ?? 'medium',
      location: taskData['location'] as String,
      category: taskData['category'] as String,
      estimatedPrice: taskData['estimatedPrice'] as double?,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }
  
  @override
  Future<TaskModel> updateTask(String taskId, Map<String, dynamic> taskData) async {
    // Имитация обновления
    await Future.delayed(Duration(milliseconds: 800));
    
    return TaskModel(
      id: taskId,
      title: taskData['title'] as String,
      description: taskData['description'] as String,
      status: taskData['status'] as String,
      priority: taskData['priority'] as String,
      location: taskData['location'] as String,
      category: taskData['category'] as String,
      estimatedPrice: taskData['estimatedPrice'] as double?,
      finalPrice: taskData['finalPrice'] as double?,
      createdAt: DateTime.now().subtract(Duration(days: 1)),
      updatedAt: DateTime.now(),
    );
  }
  
  @override
  Future<bool> deleteTask(String taskId) async {
    // Имитация удаления
    await Future.delayed(Duration(milliseconds: 500));
    
    return true;
  }
}
