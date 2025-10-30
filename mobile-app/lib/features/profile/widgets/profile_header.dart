import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import '../logic/bloc/profile_bloc.dart';
import '../logic/bloc/profile_event.dart';
import '../models/profile_model.dart';

/// Заголовок профиля с информацией о пользователе
class ProfileHeader extends StatelessWidget {
  final ProfileModel profile;

  const ProfileHeader({
    super.key,
    required this.profile,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(16.0, 24.0, 16.0, 24.0),
      decoration: BoxDecoration(
        color: theme.primaryColor,
      ),
      child: Column(
        children: [
          Row(
            children: [
              // User Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      profile.name,
                      style: GoogleFonts.roboto(
                        color: Colors.white,
                        fontSize: 18.0,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4.0),
                    Row(
                      children: [
                        const Icon(
                          Icons.location_on,
                          color: Colors.white,
                          size: 16.0,
                        ),
                        const SizedBox(width: 4.0),
                        Text(
                          profile.city,
                          style: GoogleFonts.inter(
                            color: Colors.white,
                            fontSize: 14.0,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              // Profile Image
              Container(
                width: 80.0,
                height: 80.0,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                ),
                child: ClipOval(
                  child: profile.avatarUrl != null
                      ? Image.network(
                          profile.avatarUrl!,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            return Container(
                              color: Colors.white24,
                              child: const Icon(
                                Icons.person,
                                color: Colors.white,
                                size: 40.0,
                              ),
                            );
                          },
                        )
                      : Container(
                          color: Colors.white24,
                          child: const Icon(
                            Icons.person,
                            color: Colors.white,
                            size: 40.0,
                          ),
                        ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16.0),
          // Edit Button
          Container(
            width: double.infinity,
            height: 44.0,
            child: ElevatedButton(
              onPressed: () {
                context.read<ProfileBloc>().add(const OpenEditModalEvent());
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF58A8F2),
                foregroundColor: Colors.white,
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
              ),
              child: Text(
                'Редактировать',
                style: GoogleFonts.roboto(
                  fontSize: 16.0,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
