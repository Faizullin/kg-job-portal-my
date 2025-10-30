import 'package:equatable/equatable.dart';
import 'user_model.dart';

/// Базовый класс для ответов аутентификации
abstract class AuthResponse extends Equatable {
  const AuthResponse();
}

/// Успешный ответ аутентификации
class AuthSuccess extends AuthResponse {
  final UserModel user;
  final String? accessToken;
  final String? refreshToken;
  final DateTime? expiresAt;

  const AuthSuccess({
    required this.user,
    this.accessToken,
    this.refreshToken,
    this.expiresAt,
  });

  /// Создание из JSON
  factory AuthSuccess.fromJson(Map<String, dynamic> json) {
    return AuthSuccess(
      user: UserModel.fromJson(json['user'] as Map<String, dynamic>),
      accessToken: json['accessToken'] as String?,
      refreshToken: json['refreshToken'] as String?,
      expiresAt: json['expiresAt'] != null
          ? DateTime.parse(json['expiresAt'] as String)
          : null,
    );
  }

  /// Преобразование в JSON
  Map<String, dynamic> toJson() {
    return {
      'user': user.toJson(),
      'accessToken': accessToken,
      'refreshToken': refreshToken,
      'expiresAt': expiresAt?.toIso8601String(),
    };
  }

  /// Копирование с изменениями
  AuthSuccess copyWith({
    UserModel? user,
    String? accessToken,
    String? refreshToken,
    DateTime? expiresAt,
  }) {
    return AuthSuccess(
      user: user ?? this.user,
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      expiresAt: expiresAt ?? this.expiresAt,
    );
  }

  @override
  List<Object?> get props => [user, accessToken, refreshToken, expiresAt];

  @override
  String toString() => 'AuthSuccess(user: $user)';
}

/// Ответ об ошибке аутентификации
class AuthFailure extends AuthResponse {
  final String message;
  final String? code;
  final dynamic details;

  const AuthFailure({
    required this.message,
    this.code,
    this.details,
  });

  /// Создание из JSON
  factory AuthFailure.fromJson(Map<String, dynamic> json) {
    return AuthFailure(
      message: json['message'] as String,
      code: json['code'] as String?,
      details: json['details'],
    );
  }

  /// Преобразование в JSON
  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'code': code,
      'details': details,
    };
  }

  @override
  List<Object?> get props => [message, code, details];

  @override
  String toString() => 'AuthFailure(message: $message, code: $code)';
}

/// Ответ о необходимости дополнительной верификации
class AuthPending extends AuthResponse {
  final String message;
  final String? verificationId;
  final Map<String, dynamic>? additionalData;

  const AuthPending({
    required this.message,
    this.verificationId,
    this.additionalData,
  });

  @override
  List<Object?> get props => [message, verificationId, additionalData];

  @override
  String toString() => 'AuthPending(message: $message)';
}
