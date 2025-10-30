import 'dart:async';
import 'package:dartz/dartz.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../../models/user_model.dart';
import '../../models/auth_request.dart';
import '../../models/auth_response.dart';
import '../../models/auth_error.dart';
import 'auth_data_source.dart';

/// Реализация источника данных аутентификации через Firebase
class FirebaseAuthDataSource implements AuthDataSource {
  final FirebaseAuth _firebaseAuth;
  final GoogleSignIn _googleSignIn;

  FirebaseAuthDataSource({
    FirebaseAuth? firebaseAuth,
    GoogleSignIn? googleSignIn,
  })  : _firebaseAuth = firebaseAuth ?? FirebaseAuth.instance,
        _googleSignIn = googleSignIn ?? GoogleSignIn();

  @override
  Future<Either<AuthError, AuthSuccess>> signInWithGoogle() async {
    try {
      print('Начинаем вход через Google...');
      
      // Инициация входа через Google
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      print('Google Sign-In результат: ${googleUser?.email ?? 'null'}');
      
      if (googleUser == null) {
        print('Пользователь отменил вход');
        return Left(AuthError.fromGoogleSignInException('Вход отменен пользователем'));
      }

      // Получение данных аутентификации
      print('Получаем данные аутентификации...');
      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;
      
      if (googleAuth.accessToken == null || googleAuth.idToken == null) {
        print('Не удалось получить токены от Google');
        return Left(AuthError.unknown('Не удалось получить токены аутентификации от Google'));
      }

      // Создание учетных данных Firebase
      print('Создаем учетные данные Firebase...');
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // Вход в Firebase
      print('Выполняем вход в Firebase...');
      final UserCredential userCredential = await _firebaseAuth.signInWithCredential(credential);
      
      if (userCredential.user == null) {
        print('Firebase не вернул пользователя');
        return Left(AuthError.unknown('Не удалось получить данные пользователя'));
      }

      print('Успешный вход в Firebase для пользователя: ${userCredential.user!.email}');
      
      // Получаем JWT токен из Firebase
      final jwtToken = await userCredential.user!.getIdToken();
      print('Получен JWT токен: ${jwtToken?.substring(0, 50)}...');
      
      final userModel = _mapFirebaseUserToUserModel(userCredential.user!);
      
      return Right(AuthSuccess(
        user: userModel,
        accessToken: jwtToken, // JWT токен Firebase для backend аутентификации
      ));

    } on FirebaseAuthException catch (e) {
      print('Firebase Auth Exception: ${e.code} - ${e.message}');
      return Left(AuthError.fromFirebaseAuthException(e));
    } catch (e) {
      print('Общая ошибка Google Sign-In: $e');
      return Left(AuthError.unknown('Ошибка входа через Google: ${e.toString()}'));
    }
  }

  @override
  Future<Either<AuthError, AuthSuccess>> signInWithApple() async {
    try {
      // TODO: Реализация Apple Sign In
      // Пока возвращаем ошибку что не поддерживается
      return Left(AuthError(
        type: AuthErrorType.operationNotAllowed,
        message: 'Вход через Apple пока не поддерживается',
      ));
    } catch (e) {
      return Left(AuthError.unknown('Ошибка входа через Apple: ${e.toString()}'));
    }
  }

  @override
  Future<Either<AuthError, AuthSuccess>> signInWithEmail(EmailSignInRequest request) async {
    try {
      if (!request.isValid) {
        return Left(AuthError(
          type: AuthErrorType.invalidEmail,
          message: 'Неверный формат email или пароля',
        ));
      }

      final UserCredential userCredential = await _firebaseAuth.signInWithEmailAndPassword(
        email: request.email.trim(),
        password: request.password,
      );

      if (userCredential.user == null) {
        return Left(AuthError.unknown('Не удалось получить данные пользователя'));
      }

      // Получаем JWT токен из Firebase
      final jwtToken = await userCredential.user!.getIdToken();
      print('Получен JWT токен для email входа: ${jwtToken?.substring(0, 50)}...');

      final userModel = _mapFirebaseUserToUserModel(userCredential.user!);
      
      return Right(AuthSuccess(
        user: userModel,
        accessToken: jwtToken,
      ));

    } on FirebaseAuthException catch (e) {
      return Left(AuthError.fromFirebaseAuthException(e));
    } catch (e) {
      return Left(AuthError.unknown('Ошибка входа: ${e.toString()}'));
    }
  }

  @override
  Future<Either<AuthError, AuthSuccess>> signUpWithEmail(EmailSignUpRequest request) async {
    try {
      if (!request.isValid) {
        return Left(AuthError(
          type: AuthErrorType.invalidEmail,
          message: 'Неверный формат email или пароля',
        ));
      }

      final UserCredential userCredential = await _firebaseAuth.createUserWithEmailAndPassword(
        email: request.email.trim(),
        password: request.password,
      );

      if (userCredential.user == null) {
        return Left(AuthError.unknown('Не удалось создать аккаунт'));
      }

      // Обновляем профиль если передано имя
      if (request.displayName != null && request.displayName!.trim().isNotEmpty) {
        await userCredential.user!.updateDisplayName(request.displayName!.trim());
        await userCredential.user!.reload();
      }

      // Получаем JWT токен из Firebase
      final jwtToken = await userCredential.user!.getIdToken();
      print('Получен JWT токен для регистрации: ${jwtToken?.substring(0, 50)}...');

      final userModel = _mapFirebaseUserToUserModel(userCredential.user!);
      
      return Right(AuthSuccess(
        user: userModel,
        accessToken: jwtToken,
      ));

    } on FirebaseAuthException catch (e) {
      return Left(AuthError.fromFirebaseAuthException(e));
    } catch (e) {
      return Left(AuthError.unknown('Ошибка регистрации: ${e.toString()}'));
    }
  }

  @override
  Future<Either<AuthError, Unit>> signOut() async {
    try {
      await Future.wait([
        _firebaseAuth.signOut(),
        _googleSignIn.signOut(),
      ]);
      
      return Right(unit);
    } catch (e) {
      return Left(AuthError.unknown('Ошибка выхода: ${e.toString()}'));
    }
  }

  @override
  Future<Either<AuthError, UserModel?>> getCurrentUser() async {
    try {
      final User? user = _firebaseAuth.currentUser;
      
      if (user == null) {
        return Right(null);
      }

      final userModel = _mapFirebaseUserToUserModel(user);
      return Right(userModel);
    } catch (e) {
      return Left(AuthError.unknown('Ошибка получения пользователя: ${e.toString()}'));
    }
  }

  @override
  Future<Either<AuthError, String>> getIdToken() async {
    try {
      final User? user = _firebaseAuth.currentUser;
      
      if (user == null) {
        return Left(AuthError(
          type: AuthErrorType.userNotFound,
          message: 'Пользователь не авторизован',
        ));
      }

      final token = await user.getIdToken();
      print('Получен JWT токен: ${token?.substring(0, 50)}...');
      
      return Right(token ?? '');
    } catch (e) {
      return Left(AuthError.unknown('Ошибка получения токена: ${e.toString()}'));
    }
  }

  @override
  Stream<UserModel?> get authStateChanges {
    return _firebaseAuth.authStateChanges().map((User? user) {
      return user != null ? _mapFirebaseUserToUserModel(user) : null;
    });
  }

  @override
  Future<Either<AuthError, Unit>> deleteAccount() async {
    try {
      final User? user = _firebaseAuth.currentUser;
      
      if (user == null) {
        return Left(AuthError(
          type: AuthErrorType.userNotFound,
          message: 'Пользователь не авторизован',
        ));
      }

      await user.delete();
      return Right(unit);
    } on FirebaseAuthException catch (e) {
      return Left(AuthError.fromFirebaseAuthException(e));
    } catch (e) {
      return Left(AuthError.unknown('Ошибка удаления аккаунта: ${e.toString()}'));
    }
  }

  @override
  Future<Either<AuthError, Unit>> sendPasswordResetEmail(String email) async {
    try {
      await _firebaseAuth.sendPasswordResetEmail(email: email.trim());
      return Right(unit);
    } on FirebaseAuthException catch (e) {
      return Left(AuthError.fromFirebaseAuthException(e));
    } catch (e) {
      return Left(AuthError.unknown('Ошибка отправки письма: ${e.toString()}'));
    }
  }

  @override
  Future<Either<AuthError, UserModel>> updateProfile({
    String? displayName,
    String? photoURL,
  }) async {
    try {
      final User? user = _firebaseAuth.currentUser;
      
      if (user == null) {
        return Left(AuthError(
          type: AuthErrorType.userNotFound,
          message: 'Пользователь не авторизован',
        ));
      }

      if (displayName != null) {
        await user.updateDisplayName(displayName.trim());
      }

      if (photoURL != null) {
        await user.updatePhotoURL(photoURL);
      }

      await user.reload();
      final updatedUser = _firebaseAuth.currentUser!;
      
      return Right(_mapFirebaseUserToUserModel(updatedUser));
    } on FirebaseAuthException catch (e) {
      return Left(AuthError.fromFirebaseAuthException(e));
    } catch (e) {
      return Left(AuthError.unknown('Ошибка обновления профиля: ${e.toString()}'));
    }
  }

  @override
  Future<Either<AuthError, Unit>> sendEmailVerification() async {
    try {
      final User? user = _firebaseAuth.currentUser;
      
      if (user == null) {
        return Left(AuthError(
          type: AuthErrorType.userNotFound,
          message: 'Пользователь не авторизован',
        ));
      }

      if (user.emailVerified) {
        return Left(AuthError(
          type: AuthErrorType.invalidCredential,
          message: 'Email уже подтвержден',
        ));
      }

      await user.sendEmailVerification();
      return Right(unit);
    } on FirebaseAuthException catch (e) {
      return Left(AuthError.fromFirebaseAuthException(e));
    } catch (e) {
      return Left(AuthError.unknown('Ошибка отправки подтверждения: ${e.toString()}'));
    }
  }

  /// Преобразование Firebase User в UserModel
  UserModel _mapFirebaseUserToUserModel(User firebaseUser) {
    return UserModel(
      uid: firebaseUser.uid,
      email: firebaseUser.email,
      displayName: firebaseUser.displayName,
      photoURL: firebaseUser.photoURL,
      phoneNumber: firebaseUser.phoneNumber,
      emailVerified: firebaseUser.emailVerified,
      creationTime: firebaseUser.metadata.creationTime,
      lastSignInTime: firebaseUser.metadata.lastSignInTime,
    );
  }
}
