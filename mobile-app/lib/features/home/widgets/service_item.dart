import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class ServiceItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;

  const ServiceItem({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 93.0,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(11.0),
        border: Border.all(color: Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          Padding(
            padding: EdgeInsets.only(left: 22.0),
            child: Container(
              width: 49.0,
              height: 49.0,
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(11.0),
              ),
              child: Icon(
                icon,
                color: Colors.white,
                size: 24.0,
              ),
            ),
          ),
          SizedBox(width: 12.0),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: GoogleFonts.roboto(
                    fontWeight: FontWeight.w600,
                    fontSize: 16.0,
                  ),
                ),
                SizedBox(height: 4.0),
                Text(
                  subtitle,
                  style: GoogleFonts.inter(
                    color: Color(0xFF64748B),
                    fontSize: 12.0,
                    fontWeight: FontWeight.normal,
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: EdgeInsets.only(right: 15.0),
            child: Icon(
              Icons.arrow_forward,
              color: Color(0xFF64748B),
              size: 18.0,
            ),
          ),
        ],
      ),
    );
  }
}
