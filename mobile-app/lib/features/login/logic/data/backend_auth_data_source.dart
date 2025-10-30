import 'package:dartz/dartz.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/network/api_endpoints.dart';
import '../../../../core/network/api_exceptions.dart';
import '../../models/backend_auth_request.dart';
import '../../models/backend_auth_response.dart';
import '../../models/auth_error.dart';

/// Источник данных для аутентификации через backend API
abstract class BackendAuthDataSource {
  /// Аутентификация через Firebase токен
  Future<Either<AuthError, BackendAuthResponse>> authenticateWithFirebase(String firebaseToken);
}

/// Реализация источника данных для backend API
class BackendAuthDataSourceImpl implements BackendAuthDataSource {
  final ApiClient _apiClient;

  BackendAuthDataSourceImpl({
    required ApiClient apiClient,
  }) : _apiClient = apiClient;

  @override
  Future<Either<AuthError, BackendAuthResponse>> authenticateWithFirebase(
    String firebaseToken,
  ) async {
    try {
      print('Отправляем Firebase токен на backend: ${firebaseToken.substring(0, 50)}...');
      
      final request = BackendAuthRequest(idToken: firebaseToken);
      
      final response = await _apiClient.post<Map<String, dynamic>>(
        ApiEndpoints.firebaseAuth,
        data: request.toJson(),
      );

      if (response.statusCode == 200 && response.data != null) {
        final backendResponse = BackendAuthResponse.fromJson(response.data!);
        print('Успешная аутентификация с backend. Пользователь: ${backendResponse.user.username}');
        
        return Right(backendResponse);
      } else {
        return Left(AuthError.unknown('Неожиданный ответ от сервера'));
      }
    } on DioException catch (e) {
      print('Ошибка backend аутентификации: ${e.message}');
      return Left(AuthError.fromDioException(e));
    } catch (e) {
      print('Общая ошибка backend аутентификации: $e');
      return Left(AuthError.unknown('Ошибка аутентификации: ${e.toString()}'));
    }
  }
}
