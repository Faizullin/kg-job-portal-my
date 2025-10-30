import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import '../logic/bloc/masters_bloc.dart';
import '../logic/bloc/masters_event.dart';
import '../logic/bloc/masters_state.dart';

/// Заголовок экрана мастеров
class MastersHeader extends StatelessWidget {
  const MastersHeader({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      height: 212,
      decoration: BoxDecoration(
        color: theme.primaryColor,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.max,
        children: [
          // Title and Menu Row
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 77, 16, 0),
            child: Row(
              mainAxisSize: MainAxisSize.max,
              children: [
                Text(
                  'Выберите мастера',
                  style: GoogleFonts.inter(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const Spacer(),
                const Icon(
                  Icons.menu,
                  color: Colors.white,
                  size: 24,
                ),
              ],
            ),
          ),
          // Search Bar
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 18, 16, 0),
            child: BlocBuilder<MastersBloc, MastersState>(
              builder: (context, state) {
                return Container(
                  width: double.infinity,
                  height: 39,
                  child: TextFormField(
                    textDirection: TextDirection.ltr,
                    textAlign: TextAlign.start,
                    onChanged: (value) {
                      if (value.trim().isNotEmpty) {
                        context.read<MastersBloc>().add(SearchMastersEvent(value.trim()));
                      } else {
                        context.read<MastersBloc>().add(const ClearSearchEvent());
                      }
                    },
                    decoration: InputDecoration(
                      hintText: 'Найти мастера (например: мебель, перевод)',
                      hintStyle: GoogleFonts.roboto(
                        color: const Color(0xFF64748B),
                        fontWeight: FontWeight.w400,
                        fontSize: 14,
                      ),
                      enabledBorder: const OutlineInputBorder(
                        borderSide: BorderSide.none,
                        borderRadius: BorderRadius.all(Radius.circular(8)),
                      ),
                      focusedBorder: const OutlineInputBorder(
                        borderSide: BorderSide.none,
                        borderRadius: BorderRadius.all(Radius.circular(8)),
                      ),
                      filled: true,
                      fillColor: Colors.white,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                    ),
                    style: GoogleFonts.inter(
                      color: const Color(0xFF101828),
                      fontSize: 14,
                    ),
                  ),
                );
              },
            ),
          ),
          // Statistics Row
          BlocBuilder<MastersBloc, MastersState>(
            builder: (context, state) {
              String totalMasters = '4';
              String averageRating = '4.8';
              String responseTime = '2ч';

              if (state is MastersLoadedState) {
                final stats = state.stats;
                totalMasters = stats['total_masters']?.toString() ?? '4';
                averageRating = stats['average_rating']?.toString() ?? '4.8';
                responseTime = stats['average_response_time']?.toString() ?? '2ч';
              }

              return Padding(
                padding: const EdgeInsets.fromLTRB(25, 8, 25, 0),
                child: Row(
                  mainAxisSize: MainAxisSize.max,
                  children: [
                    Column(
                      children: [
                        Text(
                          totalMasters,
                          style: GoogleFonts.inter(
                            color: Colors.white,
                            fontSize: 16.5,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'мастеров',
                          style: GoogleFonts.inter(
                            color: Colors.white,
                            fontSize: 10.5,
                            fontWeight: FontWeight.normal,
                          ),
                        ),
                      ],
                    ),
                    const Spacer(),
                    Column(
                      children: [
                        Text(
                          averageRating,
                          style: GoogleFonts.inter(
                            color: Colors.white,
                            fontSize: 16.5,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'средняя оценка',
                          style: GoogleFonts.inter(
                            color: Colors.white,
                            fontSize: 10.5,
                            fontWeight: FontWeight.normal,
                          ),
                        ),
                      ],
                    ),
                    const Spacer(),
                    Column(
                      children: [
                        Text(
                          responseTime,
                          style: GoogleFonts.inter(
                            color: Colors.white,
                            fontSize: 16.5,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'время ответа',
                          style: GoogleFonts.inter(
                            color: Colors.white,
                            fontSize: 10.5,
                            fontWeight: FontWeight.normal,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
