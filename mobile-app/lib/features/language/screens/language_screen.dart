import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class LanguageScreen extends StatelessWidget {
  const LanguageScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Язык',
          style: GoogleFonts.roboto(fontWeight: FontWeight.w600),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Text(
          'Выбор языка',
          style: GoogleFonts.roboto(fontSize: 18.0),
        ),
      ),
    );
  }
}
