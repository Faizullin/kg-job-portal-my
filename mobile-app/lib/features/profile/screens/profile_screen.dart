import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:go_router/go_router.dart';
import '../logic/bloc/profile_bloc.dart';
import '../logic/bloc/profile_event.dart';
import '../logic/bloc/profile_state.dart';
import '../logic/data/profile_data_source.dart';
import '../logic/data/profile_repository.dart';
import '../widgets/profile_header.dart';
import '../widgets/profile_menu_item.dart';
import '../widgets/edit_profile_modal.dart';
import 'notification_settings_screen.dart';
import '../../otzyvy/screens/otzyvy_screen.dart';
import '../../help/screens/help_screen.dart';

/// Экран профиля пользователя
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => ProfileBloc(
        repository: ProfileRepositoryImpl(
          dataSource: ProfileDataSourceImpl(),
        ),
      )..add(const LoadProfileEvent()),
      child: const ProfileScreenView(),
    );
  }
}

/// Вид экрана профиля
class ProfileScreenView extends StatefulWidget {
  const ProfileScreenView({super.key});

  @override
  State<ProfileScreenView> createState() => _ProfileScreenViewState();
}

class _ProfileScreenViewState extends State<ProfileScreenView> {
  bool _isModalOpen = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: theme.primaryColor,
        automaticallyImplyLeading: false,
        elevation: 0.0,
        toolbarHeight: 50.0,
        title: Text(
          'Мой профиль',
          style: GoogleFonts.inter(
            color: Colors.white,
            fontSize: 18.0,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: BlocListener<ProfileBloc, ProfileState>(
        listener: (context, state) {
          if (state is ProfileUpdatedState) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: Colors.green,
              ),
            );
          } else if (state is ProfileUpdateErrorState) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: Colors.red,
              ),
            );
          } else if (state is ProfileAccountDeletedState) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Аккаунт успешно удален'),
                backgroundColor: Colors.green,
              ),
            );
            // TODO: Navigate to login screen
          } else if (state is ProfileEditFormState && state.isModalOpen && !_isModalOpen) {
            // Показываем модальное окно только если оно еще не открыто
            _isModalOpen = true;
            _showEditProfileModal(context);
          }
        },
        child: BlocBuilder<ProfileBloc, ProfileState>(
          builder: (context, state) {
            if (state is ProfileLoadingState) {
              return const Center(
                child: CircularProgressIndicator(),
              );
            }

            if (state is ProfileErrorState) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Ошибка загрузки профиля',
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
                        context.read<ProfileBloc>().add(const LoadProfileEvent());
                      },
                      child: const Text('Повторить'),
                    ),
                  ],
                ),
              );
            }

            if (state is ProfileLoadedState) {
              return Column(
                children: [
                  // Blue Header Section
                  ProfileHeader(profile: state.profile),
                  // Menu Items Section
                  Expanded(
                    child: Container(
                      color: Colors.white,
                      child: SingleChildScrollView(
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          
                          child: Column(
                            children: [
                              ProfileMenuItem(
                                title: 'История задач',
                                onTap: () {
                                  Navigator.pushNamed(context, '/tasks');
                                },
                              ),
                              ProfileMenuItem(
                                title: 'Отзывы',
                                onTap: () {
                                  showModalBottomSheet(
                                    context: context,
                                    isScrollControlled: true,
                                    backgroundColor: Colors.transparent,
                                    builder: (BuildContext context) {
                                      return const OtzyvyModalScreen();
                                    },
                                  );
                                },
                              ),
                              ProfileMenuItem(
                                title: 'Настройка уведомлений',
                                onTap: () {
                                  showModalBottomSheet(
                                    context: context,
                                    isScrollControlled: true,
                                    backgroundColor: Colors.transparent,
                                    builder: (BuildContext context) {
                                      return const NotificationSettingsScreen();
                                    },
                                  );
                                },
                              ),
                              ProfileMenuItem(
                                title: 'Поддержка',
                                onTap: () {
                                  showModalBottomSheet(
                                    context: context,
                                    isScrollControlled: true,
                                    backgroundColor: Colors.transparent,
                                    builder: (BuildContext context) {
                                      return const HelpModalScreen();
                                    },
                                  );
                                },
                              ),
                              ProfileMenuItem(
                                title: 'О приложении',
                                onTap: () {
                                  Navigator.pushNamed(context, '/about_app');
                                },
                              ),
                              ProfileMenuItem(
                                title: 'Стать специалистом',
                                onTap: () {
                                  // TODO: Implement become specialist
                                },
                              ),
                              ProfileMenuItem(
                                title: 'Как вам приложение',
                                onTap: () {
                                  // TODO: Implement app rating
                                },
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              );
            }

            if (state is ProfileEditFormState) {
              return Column(
                children: [
                  // Blue Header Section
                  ProfileHeader(profile: state.profile),
                  // Menu Items Section
                  Expanded(
                    child: Container(
                      color: Colors.white,
                      child: SingleChildScrollView(
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            children: [
                              ProfileMenuItem(
                                title: 'История задач',
                                onTap: () {
                                  Navigator.pushNamed(context, '/tasks');
                                },
                              ),
                              ProfileMenuItem(
                                title: 'Отзывы',
                                onTap: () {
                                  showModalBottomSheet(
                                    context: context,
                                    isScrollControlled: true,
                                    backgroundColor: Colors.transparent,
                                    builder: (BuildContext context) {
                                      return const OtzyvyModalScreen();
                                    },
                                  );
                                },
                              ),
                              ProfileMenuItem(
                                title: 'Настройка уведомлений',
                                onTap: () {
                                  showModalBottomSheet(
                                    context: context,
                                    isScrollControlled: true,
                                    backgroundColor: Colors.transparent,
                                    builder: (BuildContext context) {
                                      return const NotificationSettingsScreen();
                                    },
                                  );
                                },
                              ),
                              ProfileMenuItem(
                                title: 'Поддержка',
                                onTap: () {
                                  showModalBottomSheet(
                                    context: context,
                                    isScrollControlled: true,
                                    backgroundColor: Colors.transparent,
                                    builder: (BuildContext context) {
                                      return const HelpModalScreen();
                                    },
                                  );
                                },
                              ),
                              ProfileMenuItem(
                                title: 'О приложении',
                                onTap: () {
                                  Navigator.pushNamed(context, '/about_app');
                                },
                              ),
                              ProfileMenuItem(
                                title: 'Стать специалистом',
                                onTap: () {
                                  // TODO: Implement become specialist
                                },
                              ),
                              ProfileMenuItem(
                                title: 'Как вам приложение',
                                onTap: () {
                                  // TODO: Implement app rating
                                },
                              ),
                            ],
                          ),
                        ),
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

  /// Показ модального окна редактирования профиля
  void _showEditProfileModal(BuildContext context) {
    final profileBloc = context.read<ProfileBloc>();
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (BuildContext context) {
        return BlocProvider.value(
          value: profileBloc,
          child: const EditProfileModal(),
        );
      },
    ).then((_) {
      // Закрываем модальное окно в BLoC и сбрасываем флаг
      setState(() {
        _isModalOpen = false;
      });
      context.read<ProfileBloc>().add(const CloseEditModalEvent());
    });
  }
}