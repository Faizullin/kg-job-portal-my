import 'package:equatable/equatable.dart';

/// Базовый класс для запросов аутентификации
abstract class AuthRequest extends Equatable {
  const AuthRequest();
}

/// Запрос для входа через Google
class GoogleSignInRequest extends AuthRequest {
  const GoogleSignInRequest();

  @override
  List<Object?> get props => [];

  @override
  String toString() => 'GoogleSignInRequest()';
}

/// Запрос для входа через Apple
class AppleSignInRequest extends AuthRequest {
  const AppleSignInRequest();

  @override
  List<Object?> get props => [];

  @override
  String toString() => 'AppleSignInRequest()';
}

/// Запрос для входа по email и паролю
class EmailSignInRequest extends AuthRequest {
  final String email;
  final String password;

  const EmailSignInRequest({
    required this.email,
    required this.password,
  });

  /// Валидация email
  bool get isEmailValid {
    return RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(email);
  }

  /// Валидация пароля
  bool get isPasswordValid {
    return password.isNotEmpty && password.length >= 6;
  }

  /// Проверка валидности всех полей
  bool get isValid => isEmailValid && isPasswordValid;

  /// Создание из JSON
  factory EmailSignInRequest.fromJson(Map<String, dynamic> json) {
    return EmailSignInRequest(
      email: json['email'] as String,
      password: json['password'] as String,
    );
  }

  /// Преобразование в JSON
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
    };
  }

  @override
  List<Object?> get props => [email, password];

  @override
  String toString() => 'EmailSignInRequest(email: $email)';
}

/// Запрос для регистрации
class EmailSignUpRequest extends AuthRequest {
  final String email;
  final String password;
  final String? displayName;

  const EmailSignUpRequest({
    required this.email,
    required this.password,
    this.displayName,
  });

  /// Валидация email
  bool get isEmailValid {
    return RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(email);
  }

  /// Валидация пароля
  bool get isPasswordValid {
    return password.isNotEmpty && password.length >= 6;
  }

  /// Валидация имени
  bool get isDisplayNameValid {
    return displayName == null || displayName!.trim().isNotEmpty;
  }

  /// Проверка валидности всех полей
  bool get isValid => isEmailValid && isPasswordValid && isDisplayNameValid;

  /// Создание из JSON
  factory EmailSignUpRequest.fromJson(Map<String, dynamic> json) {
    return EmailSignUpRequest(
      email: json['email'] as String,
      password: json['password'] as String,
      displayName: json['displayName'] as String?,
    );
  }

  /// Преобразование в JSON
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'displayName': displayName,
    };
  }

  @override
  List<Object?> get props => [email, password, displayName];

  @override
  String toString() => 'EmailSignUpRequest(email: $email, displayName: $displayName)';
}
