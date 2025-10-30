import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AboutAppScreen extends StatelessWidget {
  const AboutAppScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'О приложении',
          style: GoogleFonts.roboto(fontWeight: FontWeight.w600),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Text(
          'Информация о приложении',
          style: GoogleFonts.roboto(fontSize: 18.0),
        ),
      ),
    );
  }
}
