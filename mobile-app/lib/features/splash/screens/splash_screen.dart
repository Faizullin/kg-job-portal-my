import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'dart:async';

/// Экран загрузки приложения
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    
    // Автопереход на экран чатов через 3 секунды
    Timer(const Duration(seconds: 3), () {
      if (mounted) {
        // context.go('/first_impression'); // Старый маршрут - закомментирован
        context.go('/chats'); // Новый маршрут на экран чатов
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        child: Image.asset(
          'assets/images/splah.jpg',
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            // Если изображение не найдено, показываем простой экран загрузки
            return Container(
              color: const Color(0xFF2563EB),
              child: const Center(
                child: CircularProgressIndicator(
                  color: Colors.white,
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
