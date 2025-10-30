import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class WhichServiceWantScreen extends StatelessWidget {
  const WhichServiceWantScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Какую услугу',
          style: GoogleFonts.roboto(fontWeight: FontWeight.w600),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Text(
          'Какую услугу',
          style: GoogleFonts.roboto(fontSize: 18.0),
        ),
      ),
    );
  }
}
