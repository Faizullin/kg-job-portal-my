import 'profile_model.dart';

/// Ответ на запрос редактирования профиля
class EditProfileResponse {
  final ProfileModel profile;
  final String message;
  final bool success;

  const EditProfileResponse({
    required this.profile,
    required this.message,
    required this.success,
  });

  /// Создание из JSON
  factory EditProfileResponse.fromJson(Map<String, dynamic> json) {
    return EditProfileResponse(
      profile: ProfileModel.fromJson(json['profile'] as Map<String, dynamic>),
      message: json['message'] as String,
      success: json['success'] as bool,
    );
  }

  /// Конвертация в JSON
  Map<String, dynamic> toJson() {
    return {
      'profile': profile.toJson(),
      'message': message,
      'success': success,
    };
  }

  /// Создание успешного ответа
  factory EditProfileResponse.success(ProfileModel profile, {String? message}) {
    return EditProfileResponse(
      profile: profile,
      message: message ?? 'Профиль успешно обновлен',
      success: true,
    );
  }

  /// Создание ответа с ошибкой
  factory EditProfileResponse.error(String message) {
    return EditProfileResponse(
      profile: ProfileModel(
        id: '',
        name: '',
        email: '',
        phone: '',
        city: '',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      ),
      message: message,
      success: false,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is EditProfileResponse &&
        other.profile == profile &&
        other.message == message &&
        other.success == success;
  }

  @override
  int get hashCode {
    return Object.hash(profile, message, success);
  }

  @override
  String toString() {
    return 'EditProfileResponse(success: $success, message: $message)';
  }
}
