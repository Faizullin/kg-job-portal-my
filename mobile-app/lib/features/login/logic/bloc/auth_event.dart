import 'package:equatable/equatable.dart';
import '../../models/auth_request.dart';

/// Базовый класс для событий аутентификации
abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

/// Событие инициализации аутентификации (проверка текущего пользователя)
class AuthInitialized extends AuthEvent {
  const AuthInitialized();

  @override
  String toString() => 'AuthInitialized()';
}

/// Событие получения JWT токена
class GetIdTokenRequested extends AuthEvent {
  const GetIdTokenRequested();

  @override
  String toString() => 'GetIdTokenRequested()';
}

/// Событие аутентификации через backend API
class BackendAuthRequested extends AuthEvent {
  final String firebaseToken;

  const BackendAuthRequested({
    required this.firebaseToken,
  });

  @override
  List<Object?> get props => [firebaseToken];

  @override
  String toString() => 'BackendAuthRequested(firebaseToken: ${firebaseToken.substring(0, 20)}...)';
}

/// Событие входа через Google
class GoogleSignInRequested extends AuthEvent {
  const GoogleSignInRequested();

  @override
  String toString() => 'GoogleSignInRequested()';
}

/// Событие входа через Apple
class AppleSignInRequested extends AuthEvent {
  const AppleSignInRequested();

  @override
  String toString() => 'AppleSignInRequested()';
}

/// Событие входа по email и паролю
class EmailSignInRequested extends AuthEvent {
  final EmailSignInRequest request;

  const EmailSignInRequested({
    required this.request,
  });

  @override
  List<Object?> get props => [request];

  @override
  String toString() => 'EmailSignInRequested(request: $request)';
}

/// Событие регистрации по email и паролю
class EmailSignUpRequested extends AuthEvent {
  final EmailSignUpRequest request;

  const EmailSignUpRequested({
    required this.request,
  });

  @override
  List<Object?> get props => [request];

  @override
  String toString() => 'EmailSignUpRequested(request: $request)';
}

/// Событие выхода из аккаунта
class SignOutRequested extends AuthEvent {
  const SignOutRequested();

  @override
  String toString() => 'SignOutRequested()';
}

/// Событие удаления аккаунта
class DeleteAccountRequested extends AuthEvent {
  const DeleteAccountRequested();

  @override
  String toString() => 'DeleteAccountRequested()';
}

/// Событие отправки письма для сброса пароля
class PasswordResetRequested extends AuthEvent {
  final String email;

  const PasswordResetRequested({
    required this.email,
  });

  @override
  List<Object?> get props => [email];

  @override
  String toString() => 'PasswordResetRequested(email: $email)';
}

/// Событие обновления профиля пользователя
class UpdateProfileRequested extends AuthEvent {
  final String? displayName;
  final String? photoURL;

  const UpdateProfileRequested({
    this.displayName,
    this.photoURL,
  });

  @override
  List<Object?> get props => [displayName, photoURL];

  @override
  String toString() => 'UpdateProfileRequested(displayName: $displayName, photoURL: $photoURL)';
}

/// Событие отправки подтверждения email
class EmailVerificationRequested extends AuthEvent {
  const EmailVerificationRequested();

  @override
  String toString() => 'EmailVerificationRequested()';
}

/// Событие изменения состояния аутентификации (внутреннее)
class AuthStateChanged extends AuthEvent {
  final dynamic user; // UserModel?

  const AuthStateChanged({
    required this.user,
  });

  @override
  List<Object?> get props => [user];

  @override
  String toString() => 'AuthStateChanged(user: $user)';
}

/// Событие очистки ошибки
class AuthErrorCleared extends AuthEvent {
  const AuthErrorCleared();

  @override
  String toString() => 'AuthErrorCleared()';
}
