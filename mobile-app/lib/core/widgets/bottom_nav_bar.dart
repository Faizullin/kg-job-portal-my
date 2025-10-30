import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Кастомный bottom navigation bar с дизайном согласно макету
class CustomBottomNavBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const CustomBottomNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 88.0,
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10.0,
            offset: Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(
                index: 0,
                icon: 'assets/images/main.png',
                label: 'Главная',
                isActive: currentIndex == 0,
              ),
              _buildNavItem(
                index: 1,
                icon: 'assets/images/masters.png',
                label: 'Мастера',
                isActive: currentIndex == 1,
              ),
              _buildNavItem(
                index: 2,
                icon: 'assets/images/messages.png',
                label: 'Сообщения',
                isActive: currentIndex == 2,
              ),
              _buildNavItem(
                index: 3,
                icon: 'assets/images/orders.png',
                label: 'Заказы',
                isActive: currentIndex == 3,
              ),
              _buildNavItem(
                index: 4,
                icon: 'assets/images/profile.png',
                label: 'Профиль',
                isActive: currentIndex == 4,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem({
    required int index,
    required String icon,
    required String label,
    required bool isActive,
  }) {
    return GestureDetector(
      onTap: () => onTap(index),
      child: Container(
        padding: EdgeInsets.symmetric(vertical: 2.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Иконка
            Container(
              width: 20.0,
              height: 20.0,
              child: Image.asset(
                icon,
                color: isActive ? Color(0xFF2563EB) : Color(0xFF667085),
                fit: BoxFit.contain,
              ),
            ),
            SizedBox(height: 5.0),
            // Текст
            Text(
              label,
              style: GoogleFonts.inter(
                fontSize: 9.0,
                fontWeight: FontWeight.w400,
                color: isActive ? Color(0xFF2563EB) : Color(0xFF667085),
                height: 1.0,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
