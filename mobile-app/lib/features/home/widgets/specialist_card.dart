import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class SpecialistCard extends StatelessWidget {
  const SpecialistCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 62.5,
      child: Row(
        children: [
          Container(
            width: 55.0,
            height: 55.0,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
            ),
            child: ClipOval(
              child: Image.network(
                'https://picsum.photos/seed/56/600',
                fit: BoxFit.cover,
              ),
            ),
          ),
          SizedBox(width: 21.0),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Мамут Рахал',
                  style: GoogleFonts.roboto(
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  'Сборка мебели',
                  style: GoogleFonts.inter(
                    fontSize: 12.0,
                    fontWeight: FontWeight.normal,
                  ),
                ),
                SizedBox(height: 9.0),
                Row(
                  children: [
                    Icon(
                      Icons.star_rounded,
                      color: Color(0xFFFCC800),
                      size: 10.0,
                    ),
                    Text(
                      '4.8',
                      style: GoogleFonts.inter(
                        fontSize: 10.0,
                      ),
                    ),
                    SizedBox(width: 4.0),
                    Text(
                      '(127 reviews)',
                      style: GoogleFonts.inter(
                        color: Color(0xFF64748B),
                        fontSize: 10.0,
                      ),
                    ),
                    SizedBox(width: 4.0),
                    Text(
                      '1200₸/hour',
                      style: GoogleFonts.inter(
                        color: Color(0xFF1A1A1A),
                        fontSize: 10.0,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Container(
            width: 28.0,
            height: 20.0,
            decoration: BoxDecoration(
              color: Color(0xFFF0B100),
              borderRadius: BorderRadius.circular(5.0),
            ),
            child: Icon(
              Icons.star_rounded,
              color: Color(0xFFFFFBBE),
              size: 10.5,
            ),
          ),
          SizedBox(width: 2.0),
          ElevatedButton(
            onPressed: () {
              print('Button pressed ...');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: Color(0xFF101828),
              side: BorderSide(color: Color(0xFFE2E8F0)),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8.0),
              ),
              padding: EdgeInsets.symmetric(horizontal: 8.5, vertical: 0.0),
              minimumSize: Size(68.0, 28.0),
              elevation: 0.0,
            ),
            child: Text(
              'Выбрать',
              style: GoogleFonts.interTight(
                fontSize: 12.0,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
