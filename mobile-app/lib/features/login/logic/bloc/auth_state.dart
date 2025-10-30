import 'package:equatable/equatable.dart';
import '../../models/user_model.dart';
import '../../models/auth_error.dart';

/// Базовый класс для состояний аутентификации
abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

/// Начальное состояние
class AuthInitial extends AuthState {
  const AuthInitial();

  @override
  String toString() => 'AuthInitial()';
}

/// Состояние загрузки
class AuthLoading extends AuthState {
  final String? message;

  const AuthLoading({this.message});

  @override
  List<Object?> get props => [message];

  @override
  String toString() => 'AuthLoading(message: $message)';
}

/// Состояние успешной аутентификации
class AuthAuthenticated extends AuthState {
  final UserModel user;

  const AuthAuthenticated({
    required this.user,
  });

  @override
  List<Object?> get props => [user];

  @override
  String toString() => 'AuthAuthenticated(user: $user)';
}

/// Состояние отсутствия аутентификации
class AuthUnauthenticated extends AuthState {
  const AuthUnauthenticated();

  @override
  String toString() => 'AuthUnauthenticated()';
}

/// Состояние ошибки аутентификации
class AuthFailureState extends AuthState {
  final AuthError error;
  final String? previousAction;

  const AuthFailureState({
    required this.error,
    this.previousAction,
  });

  @override
  List<Object?> get props => [error, previousAction];

  @override
  String toString() => 'AuthFailureState(error: $error, previousAction: $previousAction)';
}

/// Состояние успешного получения JWT токена
class AuthTokenReceived extends AuthState {
  final String token;

  const AuthTokenReceived({
    required this.token,
  });

  @override
  List<Object?> get props => [token];

  @override
  String toString() => 'AuthTokenReceived(token: ${token.substring(0, 20)}...)';
}

/// Состояние успешного выполнения операции (например, сброс пароля)
class AuthOperationSuccess extends AuthState {
  final String message;
  final String? operationType;

  const AuthOperationSuccess({
    required this.message,
    this.operationType,
  });

  @override
  List<Object?> get props => [message, operationType];

  @override
  String toString() => 'AuthOperationSuccess(message: $message, operationType: $operationType)';
}

/// Состояние требования дополнительной верификации
class AuthVerificationRequired extends AuthState {
  final String message;
  final UserModel? user;

  const AuthVerificationRequired({
    required this.message,
    this.user,
  });

  @override
  List<Object?> get props => [message, user];

  @override
  String toString() => 'AuthVerificationRequired(message: $message, user: $user)';
}

/// Расширения для удобной работы с состояниями
extension AuthStateExtensions on AuthState {
  /// Проверка, авторизован ли пользователь
  bool get isAuthenticated => this is AuthAuthenticated;

  /// Проверка, идет ли загрузка
  bool get isLoading => this is AuthLoading;

  /// Проверка, есть ли ошибка
  bool get hasError => this is AuthFailureState;

  /// Получение пользователя (если авторизован)
  UserModel? get user {
    if (this is AuthAuthenticated) {
      return (this as AuthAuthenticated).user;
    }
    if (this is AuthVerificationRequired) {
      return (this as AuthVerificationRequired).user;
    }
    return null;
  }

  /// Получение ошибки (если есть)
  AuthError? get error {
    if (this is AuthFailureState) {
      return (this as AuthFailureState).error;
    }
    return null;
  }

  /// Получение сообщения загрузки
  String? get loadingMessage {
    if (this is AuthLoading) {
      return (this as AuthLoading).message;
    }
    return null;
  }

  /// Получение сообщения об успехе операции
  String? get successMessage {
    if (this is AuthOperationSuccess) {
      return (this as AuthOperationSuccess).message;
    }
    return null;
  }
}
