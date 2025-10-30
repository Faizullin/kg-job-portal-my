import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:go_router/go_router.dart';
import '../logic/bloc/profile_bloc.dart';
import '../logic/bloc/profile_event.dart';
import '../logic/bloc/profile_state.dart';
import '../../login/logic/bloc/auth_bloc.dart';
import '../../login/logic/bloc/auth_event.dart';
import '../../login/logic/bloc/auth_state.dart';

/// Модальное окно редактирования профиля
class EditProfileModal extends StatefulWidget {
  const EditProfileModal({super.key});

  @override
  State<EditProfileModal> createState() => _EditProfileModalState();
}

class _EditProfileModalState extends State<EditProfileModal> {
  late TextEditingController _firstNameController;
  late TextEditingController _lastNameController;
  late TextEditingController _phoneController;
  late TextEditingController _emailController;

  @override
  void initState() {
    super.initState();
    _firstNameController = _LTRTextEditingController();
    _lastNameController = _LTRTextEditingController();
    _phoneController = _LTRTextEditingController();
    _emailController = _LTRTextEditingController();
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<AuthBloc, AuthState>(
      listener: (context, state) {
        if (state is AuthUnauthenticated) {
          // После выхода перенаправляем на экран входа
          context.go('/login');
        } else if (state is AuthTokenReceived) {
          // Показываем JWT токен в диалоге
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('JWT Token'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Получен JWT токен:'),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: SelectableText(
                      state.token,
                      style: const TextStyle(fontSize: 12, fontFamily: 'monospace'),
                    ),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Закрыть'),
                ),
              ],
            ),
          );
        }
      },
      child: BlocBuilder<ProfileBloc, ProfileState>(
      builder: (context, state) {
        if (state is! ProfileEditFormState) {
          return const SizedBox.shrink();
        }

        final formData = state.formData;
        final errors = state.errors;

        // Не заполняем контроллеры автоматически - пользователь сам вводит данные

        return Container(
          height: MediaQuery.of(context).size.height * 0.9,
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(20),
              topRight: Radius.circular(20),
            ),
          ),
          child: Column(
            children: [
              // Handle bar
              Container(
                margin: const EdgeInsets.only(top: 12),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Profile Picture Section
                      Center(
                        child: Stack(
                          children: [
                            Container(
                              width: 100,
                              height: 100,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.grey[200],
                              ),
                              child: Image.asset(
                                'assets/images/profile_image.png',
                                width: 100,
                                height: 100,
                                fit: BoxFit.cover,
                              ),
                            ),
                            Positioned(
                              bottom: 0,
                              right: 0,
                              child: GestureDetector(
                                onTap: () {
                                  // TODO: Implement image picker
                                  context.read<ProfileBloc>().add(
                                    const UploadAvatarEvent(''),
                                  );
                                },
                                child: Container(
                                  width: 32,
                                  height: 32,
                                  decoration: const BoxDecoration(
                                    color: Colors.green,
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(
                                    Icons.add,
                                    color: Colors.white,
                                    size: 20,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 30),
                      
                      // First Name Field
                      _buildFormField(
                        context,
                        'Имя',
                        _firstNameController,
                        'firstName',
                        errors['firstName'],
                        (value) => context.read<ProfileBloc>().add(
                          UpdateFormFieldEvent('firstName', value),
                        ),
                      ),
                      
                      // Last Name Field
                      _buildFormField(
                        context,
                        'Фамилия',
                        _lastNameController,
                        'lastName',
                        errors['lastName'],
                        (value) => context.read<ProfileBloc>().add(
                          UpdateFormFieldEvent('lastName', value),
                        ),
                      ),
                      
                      // City Field
                      _buildDropdownField(
                        context,
                        'Город',
                        'Выберите ваш город',
                        'city',
                        errors['city'],
                        () {
                          // TODO: Implement city picker
                        },
                      ),
                      
                      // Gender Field
                      _buildDropdownField(
                        context,
                        'Пол',
                        'Выберите ваш пол',
                        'gender',
                        errors['gender'],
                        () {
                          // TODO: Implement gender picker
                        },
                      ),
                      
                      // Phone Field
                      _buildFormField(
                        context,
                        'Номер телефона',
                        _phoneController,
                        'phone',
                        errors['phone'],
                        (value) => context.read<ProfileBloc>().add(
                          UpdateFormFieldEvent('phone', value),
                        ),
                      ),
                      
                      // Email Field
                      _buildFormField(
                        context,
                        'Почта',
                        _emailController,
                        'email',
                        errors['email'],
                        (value) => context.read<ProfileBloc>().add(
                          UpdateFormFieldEvent('email', value),
                        ),
                      ),
                      
                      const SizedBox(height: 30),
                      
                      // Save Button
                      Container(
                        width: double.infinity,
                        height: 48,
                        child: ElevatedButton(
                          onPressed: () {
                            context.read<ProfileBloc>().add(const ValidateFormEvent());
                            
                            // Если нет ошибок валидации, сохраняем
                            if (errors.isEmpty) {
                              context.read<ProfileBloc>().add(UpdateProfileEvent(formData));
                              Navigator.pop(context);
                            }
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          child: Text(
                            'Сохранить',
                            style: GoogleFonts.inter(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 30),
                      
                      // Authorization Section
                      Text(
                        'Авторизация',
                        style: GoogleFonts.roboto(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: const Color(0xFF101828),
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      _buildSocialButton('Привязать Google Account', 'assets/images/Google-icon.png'),
                      const SizedBox(height: 12),
                      _buildSocialButton('Привязать Apple', Icons.apple, Colors.black),
                      
                      const SizedBox(height: 30),
                      
                      // Management Section
                      Text(
                        'Управление',
                        style: GoogleFonts.roboto(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: const Color(0xFF101828),
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      _buildActionButton('Получить JWT токен', () {
                        context.read<AuthBloc>().add(const GetIdTokenRequested());
                      }),
                      const SizedBox(height: 12),
                      _buildActionButton('Удалить аккаунт', () {
                        context.read<ProfileBloc>().add(const DeleteAccountEvent());
                      }),
                      const SizedBox(height: 12),
                      _buildActionButton('Выйти', () {
                        // Закрываем модальное окно
                        Navigator.of(context).pop();
                        // Вызываем выход из аккаунта через AuthBloc
                        context.read<AuthBloc>().add(const SignOutRequested());
                      }),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    ),
    );
  }

  Widget _buildFormField(
    BuildContext context,
    String label,
    TextEditingController controller,
    String field,
    String? error,
    Function(String) onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 14,
            fontWeight: FontWeight.w400,
            color: const Color(0xFF344054),
          ),
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          height: 48,
          decoration: BoxDecoration(
            border: Border.all(
              color: error != null ? Colors.red : const Color(0xFFE2E8F0),
            ),
            borderRadius: BorderRadius.circular(8),
          ),
          child: TextField(
            controller: controller,
            onChanged: onChanged,
            textDirection: TextDirection.ltr,
            textAlign: TextAlign.start,
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: const Color(0xFF344054),
            ),
            keyboardType: field == 'email' ? TextInputType.emailAddress : 
                         field == 'phone' ? TextInputType.phone : TextInputType.text,
            textInputAction: TextInputAction.next,
            inputFormatters: [
              FilteringTextInputFormatter.allow(RegExp(r'[a-zA-Z0-9а-яА-Я\s@._+-]')),
            ],
            decoration: InputDecoration(
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              errorText: error,
              hintText: _getHintText(field),
              hintStyle: GoogleFonts.inter(
                fontSize: 16,
                fontWeight: FontWeight.w400,
                color: const Color(0xFF94A3B8),
              ),
            ),
          ),
        ),
        const SizedBox(height: 20),
      ],
    );
  }

  String _getHintText(String field) {
    switch (field) {
      case 'firstName':
        return 'Ваше имя';
      case 'lastName':
        return 'Ваша фамилия';
      case 'phone':
        return '+7 (___) ___-__-__';
      case 'email':
        return 'example@email.com';
      default:
        return '';
    }
  }

  Widget _buildDropdownField(
    BuildContext context,
    String label,
    String value,
    String field,
    String? error,
    VoidCallback onTap,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.roboto(
            fontSize: 14,
            fontWeight: FontWeight.w400,
            color: const Color(0xFF64748B),
          ),
        ),
        const SizedBox(height: 8),
        GestureDetector(
          onTap: onTap,
          child: Container(
            width: double.infinity,
            height: 48,
            decoration: BoxDecoration(
              border: Border.all(
                color: error != null ? Colors.red : const Color(0xFFE2E8F0),
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    child: Text(
                      value,
                      textDirection: TextDirection.ltr,
                      textAlign: TextAlign.start,
                      style: GoogleFonts.roboto(
                        fontSize: 16,
                        color: const Color(0xFF1E293B),
                      ),
                    ),
                  ),
                ),
                const Icon(
                  Icons.keyboard_arrow_down,
                  color: Color(0xFF64748B),
                ),
                const SizedBox(width: 16),
              ],
            ),
          ),
        ),
        if (error != null) ...[
          const SizedBox(height: 4),
          Text(
            error,
            style: GoogleFonts.roboto(
              fontSize: 12,
              color: Colors.red,
            ),
          ),
        ],
        const SizedBox(height: 20),
      ],
    );
  }

  Widget _buildSocialButton(String text, dynamic iconOrImagePath, [Color? iconColor]) {
    return Container(
      width: double.infinity,
      height: 48,
      decoration: BoxDecoration(
        color: const Color(0xFFFAFAFA),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          const SizedBox(width: 16),
          if (iconOrImagePath is IconData)
            Icon(iconOrImagePath, color: iconColor, size: 24)
          else if (iconOrImagePath is String)
            Image.asset(
              iconOrImagePath,
              width: 21,
              height: 21,
              fit: BoxFit.contain,
              errorBuilder: (context, error, stackTrace) {
                return Icon(
                  Icons.g_mobiledata,
                  color: Colors.blue,
                  size: 21,
                );
              },
            ),
          const SizedBox(width: 12),
          Text(
            text,
            style: GoogleFonts.inter(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: const Color(0xFF323232),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(String text, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        height: 44,
        decoration: BoxDecoration(
          border: Border.all(color: const Color(0xFFE2E2E2)),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Text(
            text,
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: const Color(0xFF323232),
            ),
          ),
        ),
      ),
    );
  }
}

/// Кастомный TextEditingController с принудительным LTR направлением
class _LTRTextEditingController extends TextEditingController {
  _LTRTextEditingController({String? text}) : super(text: text);

  @override
  TextSpan buildTextSpan({
    required BuildContext context,
    TextStyle? style,
    required bool withComposing,
  }) {
    return TextSpan(
      text: text,
      style: style,
    );
  }
}
