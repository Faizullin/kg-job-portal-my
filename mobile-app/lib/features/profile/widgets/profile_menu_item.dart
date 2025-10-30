import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Элемент меню профиля
class ProfileMenuItem extends StatelessWidget {
  final String title;
  final VoidCallback onTap;

  const ProfileMenuItem({
    super.key,
    required this.title,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 1.0),
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(
          bottom: BorderSide(
            color: Color(0xFFF1F5F9),
            width: 1.0,
          ),
        ),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 0.0, vertical: 4.0),
        title: Text(
          title,
          style: GoogleFonts.roboto(
            fontWeight: FontWeight.w400,
            fontSize: 16.0,
            color: const Color(0xFF1E293B),
          ),
        ),
        trailing: const Icon(
          Icons.arrow_forward_ios,
          color: Color(0xFF64748B),
          size: 16.0,
        ),
        onTap: onTap,
      ),
    );
  }
}
