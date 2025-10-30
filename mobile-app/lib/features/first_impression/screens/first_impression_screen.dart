import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:go_router/go_router.dart';
import '../../login/logic/bloc/auth_bloc.dart';
import '../../login/logic/bloc/auth_event.dart';
import '../../login/logic/bloc/auth_state.dart';

class FirstImpressionScreen extends StatelessWidget {
  const FirstImpressionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFFF9F9F9),
      body: BlocListener<AuthBloc, AuthState>(
        listener: (context, state) {
          if (state is AuthAuthenticated) {
            // Переход на главный экран при успешной авторизации
            context.go('/');
          } else if (state is AuthFailureState) {
            // Показ ошибки
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.error.message),
                backgroundColor: Colors.red,
              ),
            );
          }
        },
        child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Center(
                child: Text(
                  'MASTER KG',
                  style: GoogleFonts.roboto(
                    fontSize: 32,
                    fontWeight: FontWeight.w700,
                    color: const Color(0xFF000000),
                    letterSpacing: 1.2,
                  ),
                ),
              ),
              const SizedBox(height: 30),
              Image.asset(
                'assets/images/first_man.png',
                width: 274,
                height: 285,
                fit: BoxFit.contain,
              ),
              Align(
                alignment: Alignment.centerLeft,
                child: RichText(
                  textAlign: TextAlign.left,
                  text: TextSpan(
                    style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF000000),
                    ),
                    children: [
                      const TextSpan(text: 'Найди работу\n'),
                      const TextSpan(
                        text: 'мечты',
                        style: TextStyle(color: Color(0xFF2563EB)),
                      ),
                      const TextSpan(text: ' здесь!'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'Изучайте все самые интересные направления\nи найдите мастера под свой запрос и интерес.',
                  style: GoogleFonts.roboto(
                    fontSize: 14,
                    fontWeight: FontWeight.w400,
                    color: const Color(0xFF524B6B),
                    height: 1.4,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: 358,
                height: 44,
                child: ElevatedButton(
                  onPressed: () {
                    context.go('/login');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    elevation: 0,
                  ),
                  child: Text(
                    'Продолжить',
                    style: GoogleFonts.roboto(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 6),
              Row(
                children: const [
                  Expanded(
                    child: Divider(
                      color: Colors.grey,
                      thickness: 1,
                      endIndent: 8, // отступ справа
                    ),
                  ),
                  Text(
                    "или",
                    style: TextStyle(
                        color: Color(0xFF9D9D9D),
                        fontWeight: FontWeight.w400,
                        fontSize: 12),
                  ),
                  Expanded(
                    child: Divider(
                      color: Colors.grey,
                      thickness: 1,
                      indent: 8, // отступ слева
                    ),
                  ),
                ],
              ),
              Row(
                children: [
                  BlocBuilder<AuthBloc, AuthState>(
                    builder: (context, state) {
                      final isLoading = state is AuthLoading;
                      
                      return GestureDetector(
                        onTap: isLoading ? null : () {
                          context.read<AuthBloc>().add(const GoogleSignInRequested());
                        },
                        child: Container(
                          width: 180,
                          height: 44,
                          decoration: BoxDecoration(
                            color: isLoading ? Color(0xFFF0F0F0) : Color(0xFFFAFAFA),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              width: 1,
                              color: Color(0xFFE2E2E2),
                            ),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.fromLTRB(16, 11.5, 16, 11.5),
                            child: Row(
                              children: [
                                if (isLoading)
                                  const SizedBox(
                                    width: 21,
                                    height: 21,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  )
                                else
                                  Image.asset(
                                    ('assets/images/Google-icon.png'),
                                    width: 21,
                                    height: 21,
                                  ),
                                const SizedBox(width: 4),
                                Text(
                                  "Войти через Google",
                                  style: GoogleFonts.inter(
                                    color: isLoading ? Color(0xFF9D9D9D) : Color(0xFF323232),
                                    fontSize: 12.0,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                  const SizedBox(width: 3),
                  BlocBuilder<AuthBloc, AuthState>(
                    builder: (context, state) {
                      final isLoading = state is AuthLoading;
                      
                      return GestureDetector(
                        onTap: isLoading ? null : () {
                          context.read<AuthBloc>().add(const AppleSignInRequested());
                        },
                        child: Container(
                          width: 176,
                          height: 44,
                          decoration: BoxDecoration(
                            color: isLoading ? Color(0xFFF0F0F0) : Color(0xFFFAFAFA),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              width: 1,
                              color: Color(0xFFE2E2E2),
                            ),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.fromLTRB(16, 11, 16, 11),
                            child: Row(
                              children: [
                                if (isLoading)
                                  const SizedBox(
                                    width: 21,
                                    height: 21,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  )
                                else
                                  Padding(
                                    padding: const EdgeInsets.only(bottom: 2),
                                    child: Icon(
                                      Icons.apple,
                                      size: 21,
                                      color: Colors.black,
                                    ),
                                  ),
                                const SizedBox(width: 5),
                                Text(
                                  "Войти через Apple",
                                  style: GoogleFonts.inter(
                                    color: isLoading ? Color(0xFF9D9D9D) : Color(0xFF323232),
                                    fontSize: 12.0,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ],
              ),
              const SizedBox(height: 22),
              Align(
                alignment: Alignment.center,
                child: GestureDetector(
                  onTap: () => _showForgotPasswordDialog(context),
                  child: Text(
                    'Забыли пароль?',
                    style: GoogleFonts.roboto(
                      fontSize: 14,
                      fontWeight: FontWeight.w400,
                      color: const Color(0xFF2563EB),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 22),

              Center(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Уже есть аккаунт? →',
                    style: GoogleFonts.roboto(
                      fontSize: 14,
                      fontWeight: FontWeight.w400,
                      color: const Color(0xFF524B6B),
                    ),
                    ),
                    GestureDetector(
                      onTap: () {
                        context.go('/login');
                      },
                      child: Text('Log in',
                        style: GoogleFonts.roboto(
                          fontSize: 14,
                          fontWeight: FontWeight.w400,
                          color: const Color(0xFF2563EB),
                        ),
                      ),
                    ),
                    
                  ],
                ),
              ),

              
            ],
          ),
        ),
        ),
      ),
    );
  }

  /// Показ диалога восстановления пароля
  void _showForgotPasswordDialog(BuildContext context) {
    final emailController = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Восстановление пароля',
          style: GoogleFonts.roboto(
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Введите email для восстановления пароля',
              style: GoogleFonts.inter(
                fontSize: 14,
                color: const Color(0xFF64748B),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(
                labelText: 'Email',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Отмена'),
          ),
          ElevatedButton(
            onPressed: () {
              if (emailController.text.trim().isNotEmpty) {
                context.read<AuthBloc>().add(
                  PasswordResetRequested(email: emailController.text.trim()),
                );
                Navigator.of(context).pop();
              }
            },
            child: const Text('Отправить'),
          ),
        ],
      ),
    );
  }
}
