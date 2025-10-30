import 'package:equatable/equatable.dart';
import 'backend_user_model.dart';

/// Ответ аутентификации от backend API
class BackendAuthResponse extends Equatable {
  final String token;
  final BackendUserModel user;

  const BackendAuthResponse({
    required this.token,
    required this.user,
  });

  /// Создание из JSON
  factory BackendAuthResponse.fromJson(Map<String, dynamic> json) {
    return BackendAuthResponse(
      token: json['token'] as String,
      user: BackendUserModel.fromJson(json['user'] as Map<String, dynamic>),
    );
  }

  /// Преобразование в JSON
  Map<String, dynamic> toJson() {
    return {
      'token': token,
      'user': user.toJson(),
    };
  }

  /// Копирование с изменениями
  BackendAuthResponse copyWith({
    String? token,
    BackendUserModel? user,
  }) {
    return BackendAuthResponse(
      token: token ?? this.token,
      user: user ?? this.user,
    );
  }

  @override
  List<Object?> get props => [token, user];

  @override
  String toString() => 'BackendAuthResponse(token: ${token.substring(0, 20)}..., user: $user)';
}
