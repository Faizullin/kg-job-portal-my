import 'package:dartz/dartz.dart';
import '../../models/user_model.dart';
import '../../models/auth_request.dart';
import '../../models/auth_response.dart';
import '../../models/auth_error.dart';

/// Абстрактный класс для источника данных аутентификации
abstract class AuthDataSource {
  /// Вход через Google
  Future<Either<AuthError, AuthSuccess>> signInWithGoogle();

  /// Вход через Apple
  Future<Either<AuthError, AuthSuccess>> signInWithApple();

  /// Вход по email и паролю
  Future<Either<AuthError, AuthSuccess>> signInWithEmail(EmailSignInRequest request);

  /// Регистрация по email и паролю
  Future<Either<AuthError, AuthSuccess>> signUpWithEmail(EmailSignUpRequest request);

  /// Выход из аккаунта
  Future<Either<AuthError, Unit>> signOut();

  /// Получение текущего пользователя
  Future<Either<AuthError, UserModel?>> getCurrentUser();

  /// Получение JWT токена текущего пользователя
  Future<Either<AuthError, String>> getIdToken();

  /// Проверка состояния аутентификации
  Stream<UserModel?> get authStateChanges;

  /// Удаление аккаунта
  Future<Either<AuthError, Unit>> deleteAccount();

  /// Отправка письма для сброса пароля
  Future<Either<AuthError, Unit>> sendPasswordResetEmail(String email);

  /// Обновление профиля пользователя
  Future<Either<AuthError, UserModel>> updateProfile({
    String? displayName,
    String? photoURL,
  });

  /// Проверка email
  Future<Either<AuthError, Unit>> sendEmailVerification();
}
