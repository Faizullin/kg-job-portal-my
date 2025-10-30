import 'package:equatable/equatable.dart';

/// Типы ошибок аутентификации
enum AuthErrorType {
  /// Пользователь не найден
  userNotFound,
  /// Неверный пароль
  wrongPassword,
  /// Недействительный email
  invalidEmail,
  /// Email уже используется
  emailAlreadyInUse,
  /// Слабый пароль
  weakPassword,
  /// Пользователь отключен
  userDisabled,
  /// Слишком много попыток
  tooManyRequests,
  /// Операция не разрешена
  operationNotAllowed,
  /// Недействительные учетные данные
  invalidCredential,
  /// Отменено пользователем
  userCancelled,
  /// Ошибка сети
  networkError,
  /// Неизвестная ошибка
  unknown,
}

/// Класс для обработки ошибок аутентификации
class AuthError extends Equatable implements Exception {
  final AuthErrorType type;
  final String message;
  final String? code;
  final dynamic originalError;

  const AuthError({
    required this.type,
    required this.message,
    this.code,
    this.originalError,
  });

  /// Создание ошибки из Firebase Auth Exception
  factory AuthError.fromFirebaseAuthException(dynamic exception) {
    final code = exception.code as String?;
    final message = exception.message as String? ?? 'Произошла ошибка аутентификации';
    
    AuthErrorType type;
    String userMessage;

    switch (code) {
      case 'user-not-found':
        type = AuthErrorType.userNotFound;
        userMessage = 'Пользователь с таким email не найден';
        break;
      case 'wrong-password':
        type = AuthErrorType.wrongPassword;
        userMessage = 'Неверный пароль';
        break;
      case 'invalid-email':
        type = AuthErrorType.invalidEmail;
        userMessage = 'Недействительный email адрес';
        break;
      case 'email-already-in-use':
        type = AuthErrorType.emailAlreadyInUse;
        userMessage = 'Этот email уже используется';
        break;
      case 'weak-password':
        type = AuthErrorType.weakPassword;
        userMessage = 'Пароль слишком слабый';
        break;
      case 'user-disabled':
        type = AuthErrorType.userDisabled;
        userMessage = 'Учетная запись отключена';
        break;
      case 'too-many-requests':
        type = AuthErrorType.tooManyRequests;
        userMessage = 'Слишком много попыток. Попробуйте позже';
        break;
      case 'operation-not-allowed':
        type = AuthErrorType.operationNotAllowed;
        userMessage = 'Операция не разрешена';
        break;
      case 'invalid-credential':
        type = AuthErrorType.invalidCredential;
        userMessage = 'Недействительные учетные данные';
        break;
      default:
        type = AuthErrorType.unknown;
        userMessage = message;
    }

    return AuthError(
      type: type,
      message: userMessage,
      code: code,
      originalError: exception,
    );
  }

  /// Создание ошибки из Google Sign In Exception
  factory AuthError.fromGoogleSignInException(dynamic exception) {
    return AuthError(
      type: AuthErrorType.userCancelled,
      message: 'Вход через Google отменен',
      originalError: exception,
    );
  }

  /// Создание из DioException
  factory AuthError.fromDioException(dynamic dioException) {
    final message = dioException.message?.toString() ?? 'Ошибка сети';
    return AuthError(
      type: AuthErrorType.networkError,
      message: message,
      originalError: dioException,
    );
  }

  /// Создание сетевой ошибки
  factory AuthError.networkError([String? customMessage]) {
    return AuthError(
      type: AuthErrorType.networkError,
      message: customMessage ?? 'Ошибка сети. Проверьте подключение к интернету',
    );
  }

  /// Создание неизвестной ошибки
  factory AuthError.unknown([String? customMessage]) {
    return AuthError(
      type: AuthErrorType.unknown,
      message: customMessage ?? 'Произошла неизвестная ошибка',
    );
  }

  /// Создание из JSON
  factory AuthError.fromJson(Map<String, dynamic> json) {
    return AuthError(
      type: AuthErrorType.values.firstWhere(
        (e) => e.toString() == json['type'],
        orElse: () => AuthErrorType.unknown,
      ),
      message: json['message'] as String,
      code: json['code'] as String?,
    );
  }

  /// Преобразование в JSON
  Map<String, dynamic> toJson() {
    return {
      'type': type.toString(),
      'message': message,
      'code': code,
    };
  }

  /// Проверка, является ли ошибка критической
  bool get isCritical {
    switch (type) {
      case AuthErrorType.networkError:
      case AuthErrorType.userCancelled:
        return false;
      default:
        return true;
    }
  }

  /// Можно ли повторить операцию
  bool get canRetry {
    switch (type) {
      case AuthErrorType.networkError:
      case AuthErrorType.tooManyRequests:
        return true;
      default:
        return false;
    }
  }

  @override
  List<Object?> get props => [type, message, code];

  @override
  String toString() => 'AuthError(type: $type, message: $message)';
}
