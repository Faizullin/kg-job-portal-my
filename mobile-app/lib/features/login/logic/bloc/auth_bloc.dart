import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../models/user_model.dart';
import '../data/auth_repository.dart';
import 'auth_event.dart';
import 'auth_state.dart';

/// BLoC для управления аутентификацией
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;
  late StreamSubscription<UserModel?> _authStateSubscription;

  AuthBloc({
    required AuthRepository authRepository,
  })  : _authRepository = authRepository,
        super(const AuthInitial()) {
    // Регистрация обработчиков событий
    on<AuthInitialized>(_onAuthInitialized);
    on<GetIdTokenRequested>(_onGetIdTokenRequested);
    on<BackendAuthRequested>(_onBackendAuthRequested);
    on<GoogleSignInRequested>(_onGoogleSignInRequested);
    on<AppleSignInRequested>(_onAppleSignInRequested);
    on<EmailSignInRequested>(_onEmailSignInRequested);
    on<EmailSignUpRequested>(_onEmailSignUpRequested);
    on<SignOutRequested>(_onSignOutRequested);
    on<DeleteAccountRequested>(_onDeleteAccountRequested);
    on<PasswordResetRequested>(_onPasswordResetRequested);
    on<UpdateProfileRequested>(_onUpdateProfileRequested);
    on<EmailVerificationRequested>(_onEmailVerificationRequested);
    on<AuthStateChanged>(_onAuthStateChanged);
    on<AuthErrorCleared>(_onAuthErrorCleared);

    // Подписка на изменения состояния аутентификации
    _authStateSubscription = _authRepository.authStateChanges.listen(
      (user) => add(AuthStateChanged(user: user)),
    );
  }

  /// Обработка инициализации аутентификации
  Future<void> _onAuthInitialized(
    AuthInitialized event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Проверка аутентификации...'));

    final result = await _authRepository.getCurrentUser();
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'initialization')),
      (user) {
        if (user != null) {
          emit(AuthAuthenticated(user: user));
        } else {
          emit(const AuthUnauthenticated());
        }
      },
    );
  }

  /// Обработка получения JWT токена
  Future<void> _onGetIdTokenRequested(
    GetIdTokenRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Получение токена...'));

    final result = await _authRepository.getIdToken();
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'get_token')),
      (token) => emit(AuthTokenReceived(token: token)),
    );
  }

  /// Обработка аутентификации через backend API
  Future<void> _onBackendAuthRequested(
    BackendAuthRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Аутентификация с сервером...'));

    final result = await _authRepository.authenticateWithBackend(event.firebaseToken);
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'backend_auth')),
      (authSuccess) => emit(AuthAuthenticated(user: authSuccess.user)),
    );
  }

  /// Обработка входа через Google
  Future<void> _onGoogleSignInRequested(
    GoogleSignInRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Вход через Google...'));

    final result = await _authRepository.signInWithGoogle();
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'google_signin')),
      (authSuccess) async {
        // После успешной Firebase аутентификации, аутентифицируемся с backend
        print('Firebase аутентификация успешна, отправляем токен на backend...');
        add(BackendAuthRequested(firebaseToken: authSuccess.accessToken ?? ''));
      },
    );
  }

  /// Обработка входа через Apple
  Future<void> _onAppleSignInRequested(
    AppleSignInRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Вход через Apple...'));

    final result = await _authRepository.signInWithApple();
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'apple_signin')),
      (authSuccess) => emit(AuthAuthenticated(user: authSuccess.user)),
    );
  }

  /// Обработка входа по email
  Future<void> _onEmailSignInRequested(
    EmailSignInRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Выполняется вход...'));

    final result = await _authRepository.signInWithEmail(event.request);
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'email_signin')),
      (authSuccess) {
        if (!authSuccess.user.emailVerified) {
          emit(AuthVerificationRequired(
            message: 'Подтвердите email для завершения входа',
            user: authSuccess.user,
          ));
        } else {
          emit(AuthAuthenticated(user: authSuccess.user));
        }
      },
    );
  }

  /// Обработка регистрации по email
  Future<void> _onEmailSignUpRequested(
    EmailSignUpRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Создание аккаунта...'));

    final result = await _authRepository.signUpWithEmail(event.request);
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'email_signup')),
      (authSuccess) {
        emit(AuthVerificationRequired(
          message: 'Аккаунт создан! Подтвердите email для завершения регистрации',
          user: authSuccess.user,
        ));
      },
    );
  }

  /// Обработка выхода из аккаунта
  Future<void> _onSignOutRequested(
    SignOutRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Выход из аккаунта...'));

    final result = await _authRepository.signOut();
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'signout')),
      (_) => emit(const AuthUnauthenticated()),
    );
  }

  /// Обработка удаления аккаунта
  Future<void> _onDeleteAccountRequested(
    DeleteAccountRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Удаление аккаунта...'));

    final result = await _authRepository.deleteAccount();
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'delete_account')),
      (_) {
        emit(const AuthOperationSuccess(
          message: 'Аккаунт успешно удален',
          operationType: 'delete_account',
        ));
        // После удаления переходим в неавторизованное состояние
        emit(const AuthUnauthenticated());
      },
    );
  }

  /// Обработка сброса пароля
  Future<void> _onPasswordResetRequested(
    PasswordResetRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Отправка письма для сброса пароля...'));

    final result = await _authRepository.sendPasswordResetEmail(event.email);
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'password_reset')),
      (_) => emit(const AuthOperationSuccess(
        message: 'Письмо для сброса пароля отправлено на ваш email',
        operationType: 'password_reset',
      )),
    );
  }

  /// Обработка обновления профиля
  Future<void> _onUpdateProfileRequested(
    UpdateProfileRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Обновление профиля...'));

    final result = await _authRepository.updateProfile(
      displayName: event.displayName,
      photoURL: event.photoURL,
    );
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'update_profile')),
      (updatedUser) {
        emit(const AuthOperationSuccess(
          message: 'Профиль успешно обновлен',
          operationType: 'update_profile',
        ));
        emit(AuthAuthenticated(user: updatedUser));
      },
    );
  }

  /// Обработка отправки подтверждения email
  Future<void> _onEmailVerificationRequested(
    EmailVerificationRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading(message: 'Отправка подтверждения email...'));

    final result = await _authRepository.sendEmailVerification();
    
    result.fold(
      (error) => emit(AuthFailureState(error: error, previousAction: 'email_verification')),
      (_) => emit(const AuthOperationSuccess(
        message: 'Письмо с подтверждением отправлено на ваш email',
        operationType: 'email_verification',
      )),
    );
  }

  /// Обработка изменения состояния аутентификации
  void _onAuthStateChanged(
    AuthStateChanged event,
    Emitter<AuthState> emit,
  ) {
    final user = event.user as UserModel?;
    
    if (user != null) {
      emit(AuthAuthenticated(user: user));
    } else {
      emit(const AuthUnauthenticated());
    }
  }

  /// Обработка очистки ошибки
  void _onAuthErrorCleared(
    AuthErrorCleared event,
    Emitter<AuthState> emit,
  ) {
    if (state is AuthFailureState) {
      emit(const AuthUnauthenticated());
    }
  }

  @override
  Future<void> close() {
    _authStateSubscription.cancel();
    return super.close();
  }
}
