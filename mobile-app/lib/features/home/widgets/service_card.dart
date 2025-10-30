import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class ServiceCard extends StatelessWidget {
  final String title;
  final String count;
  final String imageUrl;

  const ServiceCard({
    super.key,
    required this.title,
    required this.count,
    required this.imageUrl,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 155.0,
      height: 180.0,
      child: Stack(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8.0),
            child: Image.network(
              imageUrl,
              width: 200.0,
              height: 200.0,
              fit: BoxFit.cover,
            ),
          ),
          Positioned(
            bottom: 7.0,
            left: 12.0,
            child: Row(
              children: [
                Text(
                  title,
                  style: GoogleFonts.roboto(
                    color: Colors.white,
                    fontSize: 16.0,
                    fontWeight: FontWeight.normal,
                  ),
                ),
                SizedBox(width: 12.0),
                Icon(
                  Icons.people,
                  color: Colors.white,
                  size: 18.0,
                ),
                SizedBox(width: 12.0),
                Text(
                  count,
                  style: GoogleFonts.inter(
                    color: Colors.white,
                    fontSize: 12.0,
                    fontWeight: FontWeight.normal,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
