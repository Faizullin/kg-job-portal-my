import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import '../logic/bloc/tasks_bloc.dart';
import '../logic/bloc/tasks_event.dart';
import '../logic/bloc/tasks_state.dart';
import '../logic/data/tasks_data_source.dart';
import '../logic/data/tasks_repository.dart';
import '../widgets/task_card.dart';

/// Экран задач
class TasksScreen extends StatelessWidget {
  const TasksScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => TasksBloc(
        repository: TasksRepositoryImpl(
          dataSource: TasksDataSourceImpl(),
        ),
      )..add(const LoadUserTasksEvent()),
      child: const TasksScreenView(),
    );
  }
}

/// Вид экрана задач
class TasksScreenView extends StatelessWidget {
  const TasksScreenView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'История задач',
          style: GoogleFonts.roboto(fontWeight: FontWeight.w600),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () {
              _showFilterBottomSheet(context);
            },
          ),
          IconButton(
            icon: const Icon(Icons.sort),
            onPressed: () {
              _showSortBottomSheet(context);
            },
          ),
        ],
      ),
      body: BlocListener<TasksBloc, TasksState>(
        listener: (context, state) {
          if (state is TasksErrorState) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: Colors.red,
              ),
            );
          } else if (state is TasksCreatedState) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Задача "${state.newTask.title}" создана'),
                backgroundColor: Colors.green,
              ),
            );
          } else if (state is TasksUpdatedState) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Задача "${state.updatedTask.title}" обновлена'),
                backgroundColor: Colors.blue,
              ),
            );
          } else if (state is TasksDeletedState) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Задача удалена'),
                backgroundColor: Colors.orange,
              ),
            );
          }
        },
        child: BlocBuilder<TasksBloc, TasksState>(
          builder: (context, state) {
            if (state is TasksLoadingState) {
              return const Center(
                child: CircularProgressIndicator(),
              );
            }

            if (state is TasksErrorState) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.error_outline,
                      size: 64,
                      color: Colors.red,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Ошибка загрузки',
                      style: GoogleFonts.roboto(
                        fontSize: 18,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      state.message,
                      style: GoogleFonts.roboto(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        context.read<TasksBloc>().add(const LoadUserTasksEvent());
                      },
                      child: const Text('Повторить'),
                    ),
                  ],
                ),
              );
            }

            if (state is TasksEmptyState) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.assignment_outlined,
                      size: 64,
                      color: Colors.grey,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Нет задач',
                      style: GoogleFonts.roboto(
                        fontSize: 18,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      state.message,
                      style: GoogleFonts.roboto(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              );
            }

            if (state is TasksLoadedState) {
              return RefreshIndicator(
                onRefresh: () async {
                  context.read<TasksBloc>().add(const RefreshTasksEvent());
                },
                child: Column(
                  children: [
                    // Search Bar
                    if (state.searchQuery != null || state.currentFilter != null)
                      Container(
                        padding: const EdgeInsets.all(16),
                        color: Colors.grey[50],
                        child: Row(
                          children: [
                            if (state.searchQuery != null)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Theme.of(context).primaryColor.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      'Поиск: ${state.searchQuery}',
                                      style: GoogleFonts.roboto(
                                        fontSize: 12,
                                        color: Theme.of(context).primaryColor,
                                      ),
                                    ),
                                    const SizedBox(width: 4),
                                    GestureDetector(
                                      onTap: () {
                                        context.read<TasksBloc>().add(const ClearSearchEvent());
                                      },
                                      child: Icon(
                                        Icons.close,
                                        size: 16,
                                        color: Theme.of(context).primaryColor,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            if (state.currentFilter != null) ...[
                              if (state.searchQuery != null) const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.orange.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      'Фильтр: ${_getStatusDisplayName(state.currentFilter!)}',
                                      style: GoogleFonts.roboto(
                                        fontSize: 12,
                                        color: Colors.orange,
                                      ),
                                    ),
                                    const SizedBox(width: 4),
                                    GestureDetector(
                                      onTap: () {
                                        context.read<TasksBloc>().add(const ClearFiltersEvent());
                                      },
                                      child: const Icon(
                                        Icons.close,
                                        size: 16,
                                        color: Colors.orange,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                            const Spacer(),
                            TextButton(
                              onPressed: () {
                                context.read<TasksBloc>().add(const ClearFiltersEvent());
                                context.read<TasksBloc>().add(const ClearSearchEvent());
                              },
                              child: const Text('Очистить все'),
                            ),
                          ],
                        ),
                      ),
                    
                    // Tasks List
                    Expanded(
                      child: state.filteredTasks.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  const Icon(
                                    Icons.search_off,
                                    size: 64,
                                    color: Colors.grey,
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    'Задачи не найдены',
                                    style: GoogleFonts.roboto(
                                      fontSize: 18,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Попробуйте изменить фильтры или поисковый запрос',
                                    style: GoogleFonts.roboto(
                                      fontSize: 14,
                                      color: Colors.grey[600],
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ],
                              ),
                            )
                          : ListView.builder(
                              padding: const EdgeInsets.all(16),
                              itemCount: state.filteredTasks.length,
                              itemBuilder: (context, index) {
                                final task = state.filteredTasks[index];
                                return TaskCard(task: task);
                              },
                            ),
                    ),
                  ],
                ),
              );
            }

            return const SizedBox.shrink();
          },
        ),
      ),
    );
  }

  /// Показ фильтра в bottom sheet
  void _showFilterBottomSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext context) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Фильтр по статусу',
                style: GoogleFonts.roboto(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 16),
              _buildFilterOption(context, '', 'Все задачи'),
              _buildFilterOption(context, 'pending', 'В ожидании'),
              _buildFilterOption(context, 'in_progress', 'В работе'),
              _buildFilterOption(context, 'completed', 'Завершена'),
              _buildFilterOption(context, 'cancelled', 'Отменена'),
            ],
          ),
        );
      },
    );
  }

  /// Показ сортировки в bottom sheet
  void _showSortBottomSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext context) {
        return Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Сортировка',
                style: GoogleFonts.roboto(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 16),
              _buildSortOption(context, 'date', 'По дате создания'),
              _buildSortOption(context, 'priority', 'По приоритету'),
              _buildSortOption(context, 'status', 'По статусу'),
              _buildSortOption(context, 'price', 'По цене'),
            ],
          ),
        );
      },
    );
  }

  /// Создание опции фильтра
  Widget _buildFilterOption(BuildContext context, String value, String label) {
    return ListTile(
      title: Text(
        label,
        style: GoogleFonts.roboto(fontSize: 16),
      ),
      onTap: () {
        Navigator.pop(context);
        context.read<TasksBloc>().add(FilterTasksByStatusEvent(value));
      },
    );
  }

  /// Создание опции сортировки
  Widget _buildSortOption(BuildContext context, String value, String label) {
    return ListTile(
      title: Text(
        label,
        style: GoogleFonts.roboto(fontSize: 16),
      ),
      onTap: () {
        Navigator.pop(context);
        context.read<TasksBloc>().add(SortTasksEvent(value));
      },
    );
  }

  /// Получение отображаемого имени статуса
  String _getStatusDisplayName(String status) {
    switch (status) {
      case 'pending':
        return 'В ожидании';
      case 'in_progress':
        return 'В работе';
      case 'completed':
        return 'Завершена';
      case 'cancelled':
        return 'Отменена';
      default:
        return 'Неизвестно';
    }
  }
}