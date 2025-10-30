/// Константы приложения
class AppConstants {
  // API
  static const String baseUrl = 'https://api.example.com';
  static const String apiVersion = 'v1';
  
  // Timeouts
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 30000;
  
  // Storage keys
  static const String userTokenKey = 'user_token';
  static const String userDataKey = 'user_data';
  static const String themeKey = 'theme_mode';
  static const String languageKey = 'language';
  
  // Routes
  static const String homeRoute = '/home';
  static const String profileRoute = '/profile';
  static const String mastersRoute = '/masters';
  static const String tasksRoute = '/tasks';
  static const String otzyvyRoute = '/otzyvy';
  static const String languageRoute = '/language';
  static const String aboutAppRoute = '/about_app';
  static const String editProfileRoute = '/edit_profile';
  static const String termOfServiceRoute = '/term_of_service';
  static const String whatYouWantRoute = '/what_you_want';
  static const String whichServiceWantRoute = '/which_service_want';
  static const String razreshenieRoute = '/razreshenie';
}
