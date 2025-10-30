import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Экран поддержки (для роутов)
class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Поддержка',
          style: GoogleFonts.roboto(fontWeight: FontWeight.w600),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Text(
          'Поддержка',
          style: GoogleFonts.roboto(fontSize: 18.0),
        ),
      ),
    );
  }
}

/// Модальное окно поддержки (для профиля)
class HelpModalScreen extends StatelessWidget {
  const HelpModalScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.8,
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
              padding: const EdgeInsets.only(left: 16, right: 16, top: 15, bottom: 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title and subtitle
                  Text(
                    'На связи 24/7 — готовы\nпомочь в любое время.',
                    style: GoogleFonts.roboto(
                      fontSize: 24,
                      fontWeight: FontWeight.w600,
                      color: const Color(0xFF1A1A1A),
                      height: 1.2,
                    ),
                  ),
                  const SizedBox(height: 32),
                  
                  Text(
                    'Популярные вопросы',
                    style: GoogleFonts.roboto(
                      fontSize: 16,
                      color: const Color(0xFF787A7E),
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // FAQ Items
                  _buildFAQItem('Поиск подходящего специалиста'),
                  _buildFAQItem('Как добавить отзыв'),
                  _buildFAQItem('Жалоба на специалиста'),
                  _buildFAQItem('Удаление оставленного отзыва'),
                  _buildFAQItem('Как стать специалистом'),
                  _buildFAQItem('Отмена активного поиска'),
                  _buildFAQItem('Как удалить свой аккаунт'),
                  _buildFAQItem('Сообщение о подозрительных действиях'),
                  _buildFAQItem('В каких случаях отзыв не публикуется'),
                  _buildFAQItem('Действия при получении негативного отзыва'),
                  _buildFAQItem('Сроки публикации отзыва'),
                  
                  const SizedBox(height: 40),
                  
                  // Chat support button
                  Center(
                    child: Container(
                      width: 358,
                      height: 44,
                      child: ElevatedButton(
                      onPressed: () {
                        // TODO: Implement chat support
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Открытие чата поддержки...'),
                            duration: Duration(seconds: 2),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        elevation: 0,
                      ),
                      child: Text(
                        'Написать в чат поддержки',
                        style: GoogleFonts.roboto(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                  ),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFAQItem(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 24),
      child: Text(
        title,
        style: GoogleFonts.roboto(
          fontSize: 16,
          fontWeight: FontWeight.w400,
          color: const Color(0xFF1A1A1A),
        ),
      ),
    );
  }
}
