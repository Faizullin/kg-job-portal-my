/// API endpoints для приложения
class ApiEndpoints {
  // Base URL
  static const String baseUrl = 'http://194.32.141.155:8000';
  static const String apiVersion = '/api/v1';
  
  // Auth endpoints
  static const String firebaseAuth = '$apiVersion/auth/firebase/';
  static const String login = '$apiVersion/auth/login';
  static const String register = '$apiVersion/auth/register';
  static const String logout = '$apiVersion/auth/logout';
  static const String refreshToken = '$apiVersion/auth/refresh';
  static const String forgotPassword = '$apiVersion/auth/forgot-password';
  static const String resetPassword = '$apiVersion/auth/reset-password';
  static const String verifyEmail = '$apiVersion/auth/verify-email';
  
  // User/Profile endpoints
  static const String profile = '$apiVersion/user/profile';
  static const String updateProfile = '$apiVersion/user/profile';
  static const String uploadAvatar = '$apiVersion/user/avatar';
  static const String deleteAccount = '$apiVersion/user/account';
  
  // Masters endpoints
  static const String masters = '$apiVersion/masters';
  static const String mastersSearch = '$apiVersion/masters/search';
  static const String masterById = '$apiVersion/masters'; // /{id}
  static const String masterReviews = '$apiVersion/masters'; // /{id}/reviews
  static const String masterServices = '$apiVersion/masters'; // /{id}/services
  
  // Services endpoints
  static const String services = '$apiVersion/services';
  static const String serviceCategories = '$apiVersion/services/categories';
  static const String serviceById = '$apiVersion/services'; // /{id}
  
  // Orders/Tasks endpoints
  static const String orders = '$apiVersion/orders';
  static const String orderById = '$apiVersion/orders'; // /{id}
  static const String createOrder = '$apiVersion/orders';
  static const String updateOrder = '$apiVersion/orders'; // /{id}
  static const String cancelOrder = '$apiVersion/orders'; // /{id}/cancel
  static const String completeOrder = '$apiVersion/orders'; // /{id}/complete
  
  // Reviews endpoints
  static const String reviews = '$apiVersion/reviews';
  static const String createReview = '$apiVersion/reviews';
  static const String updateReview = '$apiVersion/reviews'; // /{id}
  static const String deleteReview = '$apiVersion/reviews'; // /{id}
  
  // Notifications endpoints
  static const String notifications = '$apiVersion/notifications';
  static const String markNotificationRead = '$apiVersion/notifications'; // /{id}/read
  static const String notificationSettings = '$apiVersion/user/notification-settings';
  
  // Upload endpoints
  static const String uploadFile = '$apiVersion/upload';
  static const String uploadImage = '$apiVersion/upload/image';
  static const String uploadDocument = '$apiVersion/upload/document';
  
  // App info endpoints
  static const String appVersion = '$apiVersion/app/version';
  static const String appSettings = '$apiVersion/app/settings';
  static const String help = '$apiVersion/app/help';
  static const String termsOfService = '$apiVersion/app/terms';
  static const String privacyPolicy = '$apiVersion/app/privacy';
  
  // Statistics endpoints
  static const String statistics = '$apiVersion/statistics';
  static const String userStatistics = '$apiVersion/user/statistics';
  static const String masterStatistics = '$apiVersion/masters'; // /{id}/statistics
  
  /// Получить полный URL для endpoint
  static String getFullUrl(String endpoint) {
    return '$baseUrl$endpoint';
  }
  
  /// Получить URL с параметрами
  static String getUrlWithParams(String endpoint, Map<String, dynamic> params) {
    final uri = Uri.parse(getFullUrl(endpoint));
    return uri.replace(queryParameters: params.map(
      (key, value) => MapEntry(key, value.toString())
    )).toString();
  }
  
  /// Получить URL с path параметрами
  static String getUrlWithPath(String endpoint, Map<String, dynamic> pathParams) {
    String url = endpoint;
    pathParams.forEach((key, value) {
      url = url.replaceAll('{$key}', value.toString());
    });
    return getFullUrl(url);
  }
}
