import 'package:dio/dio.dart';
import '../errors/failures.dart';

/// Исключения для работы с API
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final String? endpoint;

  const ApiException({
    required this.message,
    this.statusCode,
    this.endpoint,
  });

  @override
  String toString() {
    return 'ApiException: $message (Status: $statusCode, Endpoint: $endpoint)';
  }
}

/// Обработка ошибок Dio
class ApiExceptionHandler {
  static ApiException handleDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
        return const ApiException(
          message: 'Время ожидания соединения истекло',
          statusCode: 408,
        );
      
      case DioExceptionType.sendTimeout:
        return const ApiException(
          message: 'Время ожидания отправки истекло',
          statusCode: 408,
        );
      
      case DioExceptionType.receiveTimeout:
        return const ApiException(
          message: 'Время ожидания получения истекло',
          statusCode: 408,
        );
      
      case DioExceptionType.badCertificate:
        return const ApiException(
          message: 'Ошибка сертификата',
          statusCode: 495,
        );
      
      case DioExceptionType.badResponse:
        return _handleBadResponse(error);
      
      case DioExceptionType.cancel:
        return const ApiException(
          message: 'Запрос был отменен',
          statusCode: 499,
        );
      
      case DioExceptionType.connectionError:
        return const ApiException(
          message: 'Ошибка подключения к серверу',
          statusCode: 503,
        );
      
      case DioExceptionType.unknown:
      default:
        return const ApiException(
          message: 'Неизвестная ошибка сети',
          statusCode: 500,
        );
    }
  }

  static ApiException _handleBadResponse(DioException error) {
    final statusCode = error.response?.statusCode ?? 500;
    final endpoint = error.requestOptions.path;
    
    // Попытка получить сообщение об ошибке от сервера
    String message = 'Ошибка сервера';
    
    try {
      final responseData = error.response?.data;
      if (responseData is Map<String, dynamic>) {
        message = responseData['message'] ?? 
                 responseData['error'] ?? 
                 responseData['detail'] ?? 
                 message;
      }
    } catch (e) {
      // Если не удалось распарсить ответ, используем стандартное сообщение
    }

    // Специальные обработки для разных статус кодов
    switch (statusCode) {
      case 400:
        message = 'Некорректный запрос';
        break;
      case 401:
        message = 'Необходима авторизация';
        break;
      case 403:
        message = 'Доступ запрещен';
        break;
      case 404:
        message = 'Ресурс не найден';
        break;
      case 422:
        message = 'Ошибка валидации данных';
        break;
      case 429:
        message = 'Слишком много запросов';
        break;
      case 500:
        message = 'Внутренняя ошибка сервера';
        break;
      case 502:
        message = 'Ошибка шлюза';
        break;
      case 503:
        message = 'Сервис недоступен';
        break;
      case 504:
        message = 'Время ожидания шлюза истекло';
        break;
    }

    return ApiException(
      message: message,
      statusCode: statusCode,
      endpoint: endpoint,
    );
  }

  /// Преобразование ApiException в Failure
  static Failure toFailure(ApiException exception) {
    switch (exception.statusCode) {
      case 401:
        return const AuthFailure(message: 'Требуется авторизация');
      case 403:
        return const AuthFailure(message: 'Доступ запрещен');
      case 404:
        return const NotFoundFailure(message: 'Ресурс не найден');
      case 422:
        return const ValidationFailure(message: 'Ошибка валидации данных');
      case 429:
        return const NetworkFailure(message: 'Слишком много запросов');
      case 500:
      case 502:
      case 503:
      case 504:
        return const ServerFailure(message: 'Ошибка сервера');
      default:
        return NetworkFailure(message: exception.message);
    }
  }
}

/// Расширение для Dio для удобной обработки ошибок
extension DioErrorExtension on DioException {
  ApiException toApiException() {
    return ApiExceptionHandler.handleDioError(this);
  }
  
  Failure toFailure() {
    return ApiExceptionHandler.toFailure(toApiException());
  }
}
