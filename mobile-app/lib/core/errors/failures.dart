/// Базовые классы ошибок
abstract class Failure {
  final String message;
  final String? code;
  
  const Failure({
    required this.message,
    this.code,
  });
}

/// Ошибки сервера
class ServerFailure extends Failure {
  const ServerFailure({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}

/// Ошибки сети
class NetworkFailure extends Failure {
  const NetworkFailure({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}

/// Ошибки валидации
class ValidationFailure extends Failure {
  const ValidationFailure({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}

/// Ошибки кэша
class CacheFailure extends Failure {
  const CacheFailure({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}

class AuthFailure extends Failure {
  const AuthFailure({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}

/// Ошибки "не найдено"
class NotFoundFailure extends Failure {
  const NotFoundFailure({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}

/// Неизвестные ошибки
class UnknownFailure extends Failure {
  const UnknownFailure({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}
