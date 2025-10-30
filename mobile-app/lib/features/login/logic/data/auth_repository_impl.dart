import 'package:dartz/dartz.dart';
import '../../models/user_model.dart';
import '../../models/auth_request.dart';
import '../../models/auth_response.dart';
import '../../models/auth_error.dart';
import '../../models/backend_auth_response.dart';
import 'auth_repository.dart';
import 'auth_data_source.dart';
import 'backend_auth_data_source.dart';

/// Реализация репозитория аутентификации
class AuthRepositoryImpl implements AuthRepository {
  final AuthDataSource _authDataSource;
  final BackendAuthDataSource _backendAuthDataSource;

  AuthRepositoryImpl({
    required AuthDataSource authDataSource,
    required BackendAuthDataSource backendAuthDataSource,
  }) : _authDataSource = authDataSource,
       _backendAuthDataSource = backendAuthDataSource;

  @override
  Future<Either<AuthError, AuthSuccess>> signInWithGoogle() async {
    try {
      return await _authDataSource.signInWithGoogle();
    } catch (e) {
      return Left(AuthError.networkError('Ошибка сети при входе через Google'));
    }
  }

  @override
  Future<Either<AuthError, AuthSuccess>> signInWithApple() async {
    try {
      return await _authDataSource.signInWithApple();
    } catch (e) {
      return Left(AuthError.networkError('Ошибка сети при входе через Apple'));
    }
  }

  @override
  Future<Either<AuthError, AuthSuccess>> signInWithEmail(EmailSignInRequest request) async {
    try {
      // Дополнительная валидация на уровне репозитория
      if (!request.isValid) {
        return Left(AuthError(
          type: AuthErrorType.invalidEmail,
          message: 'Неверный формат email или пароля',
        ));
      }

      return await _authDataSource.signInWithEmail(request);
    } catch (e) {
      return Left(AuthError.networkError('Ошибка сети при входе'));
    }
  }

  @override
  Future<Either<AuthError, AuthSuccess>> signUpWithEmail(EmailSignUpRequest request) async {
    try {
      // Дополнительная валидация на уровне репозитория
      if (!request.isValid) {
        return Left(AuthError(
          type: AuthErrorType.invalidEmail,
          message: 'Неверный формат данных для регистрации',
        ));
      }

      return await _authDataSource.signUpWithEmail(request);
    } catch (e) {
      return Left(AuthError.networkError('Ошибка сети при регистрации'));
    }
  }

  @override
  Future<Either<AuthError, Unit>> signOut() async {
    try {
      return await _authDataSource.signOut();
    } catch (e) {
      return Left(AuthError.networkError('Ошибка сети при выходе'));
    }
  }

  @override
  Future<Either<AuthError, UserModel?>> getCurrentUser() async {
    try {
      return await _authDataSource.getCurrentUser();
    } catch (e) {
      return Left(AuthError.networkError('Ошибка получения данных пользователя'));
    }
  }

  @override
  Future<Either<AuthError, String>> getIdToken() async {
    try {
      return await _authDataSource.getIdToken();
    } catch (e) {
      return Left(AuthError.networkError('Ошибка получения токена'));
    }
  }

  @override
  Future<Either<AuthError, AuthSuccess>> authenticateWithBackend(String firebaseToken) async {
    try {
      final result = await _backendAuthDataSource.authenticateWithFirebase(firebaseToken);
      
      return result.fold(
        (error) => Left(error),
        (backendResponse) {
          // Конвертируем backend пользователя в наш UserModel
          final userModel = UserModel(
            uid: backendResponse.user.id.toString(),
            email: backendResponse.user.email,
            displayName: backendResponse.user.name,
            photoURL: null,
            phoneNumber: null,
            emailVerified: backendResponse.user.isActive,
            creationTime: DateTime.now(),
            lastSignInTime: DateTime.now(),
          );
          
          return Right(AuthSuccess(
            user: userModel,
            accessToken: backendResponse.token,
          ));
        },
      );
    } catch (e) {
      return Left(AuthError.networkError('Ошибка сети при аутентификации'));
    }
  }

  @override
  Stream<UserModel?> get authStateChanges {
    return _authDataSource.authStateChanges;
  }

  @override
  Future<Either<AuthError, Unit>> deleteAccount() async {
    try {
      return await _authDataSource.deleteAccount();
    } catch (e) {
      return Left(AuthError.networkError('Ошибка сети при удалении аккаунта'));
    }
  }

  @override
  Future<Either<AuthError, Unit>> sendPasswordResetEmail(String email) async {
    try {
      // Валидация email
      final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
      if (!emailRegex.hasMatch(email.trim())) {
        return Left(AuthError(
          type: AuthErrorType.invalidEmail,
          message: 'Неверный формат email адреса',
        ));
      }

      return await _authDataSource.sendPasswordResetEmail(email.trim());
    } catch (e) {
      return Left(AuthError.networkError('Ошибка сети при отправке письма'));
    }
  }

  @override
  Future<Either<AuthError, UserModel>> updateProfile({
    String? displayName,
    String? photoURL,
  }) async {
    try {
      // Валидация данных
      if (displayName != null && displayName.trim().isEmpty) {
        return Left(AuthError(
          type: AuthErrorType.invalidCredential,
          message: 'Имя не может быть пустым',
        ));
      }

      if (photoURL != null && photoURL.trim().isEmpty) {
        return Left(AuthError(
          type: AuthErrorType.invalidCredential,
          message: 'URL фото не может быть пустым',
        ));
      }

      return await _authDataSource.updateProfile(
        displayName: displayName?.trim(),
        photoURL: photoURL?.trim(),
      );
    } catch (e) {
      return Left(AuthError.networkError('Ошибка сети при обновлении профиля'));
    }
  }

  @override
  Future<Either<AuthError, Unit>> sendEmailVerification() async {
    try {
      return await _authDataSource.sendEmailVerification();
    } catch (e) {
      return Left(AuthError.networkError('Ошибка сети при отправке подтверждения'));
    }
  }

  @override
  bool get isAuthenticated {
    // Получаем текущего пользователя синхронно через DataSource
    // В реальном приложении можно кешировать это состояние
    return currentUserId != null;
  }

  @override
  String? get currentUserId {
    // Этот метод должен быть синхронным, поэтому используем Firebase.currentUser
    // В более сложной архитектуре можно использовать StateManager или кеширование
    try {
      // Поскольку мы не можем сделать async call здесь,
      // используем прямой доступ к Firebase (нарушение Clean Architecture для удобства)
      return null; // TODO: Реализовать через синхронное получение пользователя
    } catch (e) {
      return null;
    }
  }
}
