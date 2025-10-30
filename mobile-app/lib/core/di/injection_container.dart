import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../../features/login/logic/data/auth_data_source.dart';
import '../../features/login/logic/data/firebase_auth_data_source.dart';
import '../../features/login/logic/data/backend_auth_data_source.dart';
import '../../features/login/logic/data/auth_repository.dart';
import '../../features/login/logic/data/auth_repository_impl.dart';
import '../../features/login/logic/bloc/auth_bloc.dart';
import '../network/api_client.dart';

/// Контейнер для управления зависимостями
class InjectionContainer {
  static InjectionContainer? _instance;
  static InjectionContainer get instance => _instance ??= InjectionContainer._();
  
  InjectionContainer._();

  // Сервисы
  late final FirebaseAuth _firebaseAuth;
  late final GoogleSignIn _googleSignIn;
  late final ApiClient _apiClient;
  
  // Data Sources
  late final AuthDataSource _authDataSource;
  late final BackendAuthDataSource _backendAuthDataSource;
  
  // Repositories
  late final AuthRepository _authRepository;
  
  // BLoCs
  AuthBloc? _authBloc;

  /// Инициализация всех зависимостей
  void init() {
    // Инициализация внешних сервисов
    _firebaseAuth = FirebaseAuth.instance;
    _googleSignIn = GoogleSignIn(
      clientId: '1026990413187-6r35bibk6v2u1k3i610ga3n9jncna2qb.apps.googleusercontent.com',
      scopes: [
        'email',
        'profile',
      ],
    );
    _apiClient = ApiClient();

    // Инициализация Data Sources
    _authDataSource = FirebaseAuthDataSource(
      firebaseAuth: _firebaseAuth,
      googleSignIn: _googleSignIn,
    );
    _backendAuthDataSource = BackendAuthDataSourceImpl(
      apiClient: _apiClient,
    );

    // Инициализация Repositories
    _authRepository = AuthRepositoryImpl(
      authDataSource: _authDataSource,
      backendAuthDataSource: _backendAuthDataSource,
    );
  }

  /// Получение AuthRepository
  AuthRepository get authRepository => _authRepository;

  /// Получение AuthBloc (singleton)
  AuthBloc get authBloc {
    _authBloc ??= AuthBloc(authRepository: _authRepository);
    return _authBloc!;
  }

  /// Очистка ресурсов
  void dispose() {
    _authBloc?.close();
    _authBloc = null;
  }
}
