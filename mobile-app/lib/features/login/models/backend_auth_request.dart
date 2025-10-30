import 'package:equatable/equatable.dart';

/// Запрос аутентификации через Firebase в backend
class BackendAuthRequest extends Equatable {
  final String idToken;

  const BackendAuthRequest({
    required this.idToken,
  });

  /// Создание из JSON
  factory BackendAuthRequest.fromJson(Map<String, dynamic> json) {
    return BackendAuthRequest(
      idToken: json['id_token'] as String,
    );
  }

  /// Преобразование в JSON
  Map<String, dynamic> toJson() {
    return {
      'id_token': idToken,
    };
  }

  @override
  List<Object?> get props => [idToken];

  @override
  String toString() => 'BackendAuthRequest(idToken: ${idToken.substring(0, 20)}...)';
}
