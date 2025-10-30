import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import '../logic/bloc/masters_bloc.dart';
import '../logic/bloc/masters_event.dart';
import '../logic/bloc/masters_state.dart';
import '../logic/data/masters_data_source.dart';
import '../logic/data/masters_repository.dart';
import '../models/masters_search_request.dart';
import '../widgets/masters_header.dart';
import '../widgets/service_category_card.dart';
import '../widgets/master_card.dart';

/// Экран мастеров
class MastersScreen extends StatelessWidget {
  const MastersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => MastersBloc(
        repository: MastersRepositoryImpl(
          dataSource: MastersDataSourceImpl(),
        ),
      )..add(const LoadMastersEvent(MastersSearchRequest())),
      child: const MastersScreenView(),
    );
  }
}

/// Вид экрана мастеров
class MastersScreenView extends StatelessWidget {
  const MastersScreenView({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: Colors.white,
      body: BlocListener<MastersBloc, MastersState>(
        listener: (context, state) {
          if (state is MastersErrorState) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: Colors.red,
              ),
            );
          } else if (state is MasterSelectedState) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Выбран мастер: ${state.selectedMaster.name}'),
                backgroundColor: Colors.green,
              ),
            );
          }
        },
        child: BlocBuilder<MastersBloc, MastersState>(
          builder: (context, state) {
            if (state is MastersLoadingState) {
              return const Center(
                child: CircularProgressIndicator(),
              );
            }

            if (state is MastersErrorState) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
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
                        context.read<MastersBloc>().add(
                          const LoadMastersEvent(MastersSearchRequest()),
                        );
                      },
                      child: const Text('Повторить'),
                    ),
                  ],
                ),
              );
            }

            if (state is MastersLoadedState || 
                state is MastersSearchingState || 
                state is MastersFilteringState ||
                state is MastersEmptyState) {
              
              List<dynamic> categories = [];
              List<dynamic> masters = [];

              if (state is MastersLoadedState) {
                categories = state.categories;
                masters = state.masters;
              } else if (state is MastersSearchingState) {
                categories = state.categories;
                masters = state.masters;
              } else if (state is MastersFilteringState) {
                categories = state.categories;
                masters = state.masters;
              } else if (state is MastersEmptyState) {
                categories = state.categories;
                masters = [];
              }

              return Column(
                children: [
                  // Blue Header Section
                  const MastersHeader(),
                  // Scrollable Content
                  Expanded(
                    child: SingleChildScrollView(
                      child: Column(
                        children: [
                          // Service Categories Section
                          Container(
                            width: double.infinity,
                            height: 210,
                            decoration: BoxDecoration(
                              color: const Color(0xFFF8F9FA),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.fromLTRB(16, 8, 0, 8),
                              child: SingleChildScrollView(
                                scrollDirection: Axis.horizontal,
                                child: Column(
                                  children: [
                                    // First Row
                                    Row(
                                      children: categories.take(3).map((category) {
                                        return Padding(
                                          padding: const EdgeInsets.only(right: 10),
                                          child: ServiceCategoryCard(
                                            category: category,
                                            onTap: () {
                                              context.read<MastersBloc>().add(
                                                FilterMastersByCategoryEvent(category.id),
                                              );
                                            },
                                          ),
                                        );
                                      }).toList(),
                                    ),
                                    const SizedBox(height: 10),
                                    // Second Row
                                    if (categories.length > 3)
                                      Row(
                                        children: categories.skip(3).take(3).map((category) {
                                          return Padding(
                                            padding: const EdgeInsets.only(right: 10),
                                            child: ServiceCategoryCard(
                                              category: category,
                                              onTap: () {
                                                context.read<MastersBloc>().add(
                                                  FilterMastersByCategoryEvent(category.id),
                                                );
                                              },
                                            ),
                                          );
                                        }).toList(),
                                      ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          // Masters Section
                          if (state is MastersEmptyState)
                            Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                children: [
                                  const Icon(
                                    Icons.search_off,
                                    size: 64,
                                    color: Colors.grey,
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    'Мастера не найдены',
                                    style: GoogleFonts.roboto(
                                      fontSize: 18,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Попробуйте изменить поисковый запрос или фильтры',
                                    style: GoogleFonts.roboto(
                                      fontSize: 14,
                                      color: Colors.grey[600],
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 16),
                                  ElevatedButton(
                                    onPressed: () {
                                      context.read<MastersBloc>().add(const ClearSearchEvent());
                                    },
                                    child: const Text('Очистить поиск'),
                                  ),
                                ],
                              ),
                            )
                          else if (masters.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.all(16),
                              child: MasterCard(master: masters.first),
                            ),
                        ],
                      ),
                    ),
                  ),
                ],
              );
            }

            return const SizedBox.shrink();
          },
        ),
      ),
    );
  }
}