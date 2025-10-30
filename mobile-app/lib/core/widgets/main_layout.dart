import 'package:flutter/material.dart';
import 'bottom_nav_bar.dart';
import '../../features/home/screens/home_screen.dart';
import '../../features/masters/screens/masters_screen.dart';
import '../../features/profile/screens/profile_screen.dart';

/// Главный layout с bottom navigation
class MainLayout extends StatefulWidget {
  const MainLayout({super.key});

  @override
  State<MainLayout> createState() => _MainLayoutState();
}

class _MainLayoutState extends State<MainLayout> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    HomeScreen(),
    MastersScreen(),
    _buildPlaceholderScreen('Сообщения'),
    _buildPlaceholderScreen('Заказы'),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: CustomBottomNavBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
      ),
    );
  }

  static Widget _buildPlaceholderScreen(String title) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          title,
          style: TextStyle(
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Text(
          'Страница $title',
          style: TextStyle(fontSize: 18.0),
        ),
      ),
    );
  }
}
