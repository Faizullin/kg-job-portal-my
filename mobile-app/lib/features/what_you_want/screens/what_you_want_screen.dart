import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class WhatYouWantScreen extends StatelessWidget {
  const WhatYouWantScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Что вы хотите',
          style: GoogleFonts.roboto(fontWeight: FontWeight.w600),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Text(
          'Что вы хотите',
          style: GoogleFonts.roboto(fontSize: 18.0),
        ),
      ),
    );
  }
}
