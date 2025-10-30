import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class TermOfServiceScreen extends StatelessWidget {
  const TermOfServiceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Условия использования',
          style: GoogleFonts.roboto(fontWeight: FontWeight.w600),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Text(
          'Условия использования',
          style: GoogleFonts.roboto(fontSize: 18.0),
        ),
      ),
    );
  }
}
