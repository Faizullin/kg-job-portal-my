import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import '../logic/bloc/masters_bloc.dart';
import '../logic/bloc/masters_event.dart';
import '../models/master_model.dart';
import '../screens/about_master_screen.dart';

/// Карточка мастера
class MasterCard extends StatelessWidget {
  final MasterModel master;

  const MasterCard({
    super.key,
    required this.master,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 421,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(11),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
        child: Column(
          children: [
            // Master Profile Section
            Row(
              children: [
                Container(
                  width: 55,
                  height: 55,
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                  ),
                  child: ClipOval(
                    child: master.avatarUrl != null
                        ? Image.network(
                            master.avatarUrl!,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                color: Colors.grey[200],
                                child: const Icon(
                                  Icons.person,
                                  color: Colors.grey,
                                  size: 30,
                                ),
                              );
                            },
                          )
                        : Container(
                            color: Colors.grey[200],
                            child: const Icon(
                              Icons.person,
                              color: Colors.grey,
                              size: 30,
                            ),
                          ),
                  ),
                ),
                const SizedBox(width: 21),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              master.name,
                              style: GoogleFonts.roboto(
                                fontWeight: FontWeight.w500,
                                fontSize: 16,
                              ),
                            ),
                          ),
                          const Icon(
                            Icons.favorite_border,
                            color: Color(0xFF101828),
                            size: 16,
                          ),
                        ],
                      ),
                      Text(
                        master.specialty,
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: const Color(0xFF64748B),
                        ),
                      ),
                      const SizedBox(height: 9),
                      Row(
                        children: [
                          const Icon(
                            Icons.star_rounded,
                            color: Color(0xFFFCC800),
                            size: 10,
                          ),
                          const SizedBox(width: 2),
                          Text(
                            master.rating.toString(),
                            style: GoogleFonts.inter(
                              fontSize: 10,
                            ),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '(${master.reviewCount} reviews)',
                            style: GoogleFonts.inter(
                              fontSize: 10,
                              color: const Color(0xFF64748B),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            // Portfolio Section
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Примеры работ',
                style: GoogleFonts.inter(
                  fontSize: 12,
                ),
              ),
            ),
            const SizedBox(height: 7),
            Container(
              width: double.infinity,
              height: 46,
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: master.portfolioImages.map((imageUrl) {
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.network(
                          imageUrl,
                          width: 56,
                          height: 56,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            return Container(
                              width: 56,
                              height: 56,
                              color: Colors.grey[200],
                              child: const Icon(
                                Icons.image_not_supported,
                                color: Colors.grey,
                                size: 20,
                              ),
                            );
                          },
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),
            const SizedBox(height: 14),
            // Skills Section
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Что умеет',
                style: GoogleFonts.inter(
                  fontSize: 12,
                ),
              ),
            ),
            const SizedBox(height: 4),
            Row(
              children: master.skills.take(1).map((skill) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    skill,
                    style: GoogleFonts.inter(
                      fontSize: 10,
                      color: const Color(0xFF1A1A1A),
                    ),
                  ),
                );
              }).toList(),
            ),
            const Divider(thickness: 1, color: Color(0xFFE2E8F0)),
            // Stats Section
            Padding(
              padding: const EdgeInsets.fromLTRB(25, 8, 25, 0),
              child: Row(
                children: [
                  Column(
                    children: [
                      Text(
                        master.completedJobs.toString(),
                        style: GoogleFonts.inter(
                          color: const Color(0xFF1A1A1A),
                          fontSize: 12.5,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'работ',
                        style: GoogleFonts.inter(
                          color: const Color(0xFF64748B),
                          fontSize: 10.5,
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),
                  Column(
                    children: [
                      Text(
                        master.hourlyRate,
                        style: GoogleFonts.inter(
                          color: const Color(0xFF1A1A1A),
                          fontSize: 12.5,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'за час',
                        style: GoogleFonts.inter(
                          color: const Color(0xFF64748B),
                          fontSize: 10.5,
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),
                  Column(
                    children: [
                      Text(
                        'Ответ',
                        style: GoogleFonts.inter(
                          color: const Color(0xFF1A1A1A),
                          fontSize: 12.5,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        master.responseTime,
                        style: GoogleFonts.inter(
                          color: const Color(0xFF64748B),
                          fontSize: 10.5,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const Divider(thickness: 1, color: Color(0xFFE2E8F0)),
            // Location and Status
            Row(
              children: [
                const Icon(
                  Icons.location_on_outlined,
                  color: Color(0xFF64748B),
                  size: 16,
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    master.location,
                    style: GoogleFonts.inter(
                      color: const Color(0xFF64748B),
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(
                  Icons.access_time_filled,
                  color: Color(0xFF64748B),
                  size: 16,
                ),
                const SizedBox(width: 4),
                Text(
                  master.isOnline ? 'Сейчас онлайн' : 'Был онлайн недавно',
                  style: GoogleFonts.inter(
                    color: const Color(0xFF64748B),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 21),
            // Action Buttons
            Row(
              children: [
                Expanded(
                  child: GestureDetector(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => AboutMasterScreen(master: master),
                        ),
                      );
                    },
                    child: Container(
                      height: 28,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(5),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.remove_red_eye_outlined,
                            color: Color(0xFF101828),
                            size: 18,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Посмотреть',
                            style: GoogleFonts.inter(
                              color: const Color(0xFF1A1A1A),
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: GestureDetector(
                    onTap: () {
                      context.read<MastersBloc>().add(SelectMasterEvent(master.id));
                    },
                    child: Container(
                      height: 28,
                      decoration: BoxDecoration(
                        color: Theme.of(context).primaryColor,
                        borderRadius: BorderRadius.circular(5),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.work_outline,
                            color: Colors.white,
                            size: 18,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Выбрать',
                            style: GoogleFonts.inter(
                              color: Colors.white,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 11),
                Container(
  width: 33.5,
  height: 28,
  decoration: BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(5),
    border: Border.all(
      color: const Color(0xFFE2E8F0),
      width: 1,
      strokeAlign: BorderSide.strokeAlignInside,
    ),
  ),
  child: Center(
    child: Image.asset(
      'assets/images/chat.png',
      width: 14,
      height: 14,
    ),
  ),
),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
