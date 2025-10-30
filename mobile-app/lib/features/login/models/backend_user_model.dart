import 'package:equatable/equatable.dart';

/// Модель пользователя от backend API
class BackendUserModel extends Equatable {
  final int id;
  final String username;
  final String email;
  final String name;
  final String userRole;
  final List<String> groups;
  final List<String> permissions;
  final bool isActive;
  final bool isStaff;
  final bool isSuperuser;

  const BackendUserModel({
    required this.id,
    required this.username,
    required this.email,
    required this.name,
    required this.userRole,
    required this.groups,
    required this.permissions,
    required this.isActive,
    required this.isStaff,
    required this.isSuperuser,
  });

  /// Создание из JSON
  factory BackendUserModel.fromJson(Map<String, dynamic> json) {
    return BackendUserModel(
      id: json['id'] as int,
      username: json['username'] as String? ?? '',
      email: json['email'] as String? ?? '',
      name: json['name'] as String? ?? '',
      userRole: json['user_role'] as String? ?? 'client',
      groups: (json['groups'] as List<dynamic>?)?.cast<String>() ?? [],
      permissions: (json['permissions'] as List<dynamic>?)?.cast<String>() ?? [],
      isActive: json['is_active'] as bool? ?? false,
      isStaff: json['is_staff'] as bool? ?? false,
      isSuperuser: json['is_superuser'] as bool? ?? false,
    );
  }

  /// Преобразование в JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'name': name,
      'user_role': userRole,
      'groups': groups,
      'permissions': permissions,
      'is_active': isActive,
      'is_staff': isStaff,
      'is_superuser': isSuperuser,
    };
  }

  /// Копирование с изменениями
  BackendUserModel copyWith({
    int? id,
    String? username,
    String? email,
    String? name,
    String? userRole,
    List<String>? groups,
    List<String>? permissions,
    bool? isActive,
    bool? isStaff,
    bool? isSuperuser,
  }) {
    return BackendUserModel(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      name: name ?? this.name,
      userRole: userRole ?? this.userRole,
      groups: groups ?? this.groups,
      permissions: permissions ?? this.permissions,
      isActive: isActive ?? this.isActive,
      isStaff: isStaff ?? this.isStaff,
      isSuperuser: isSuperuser ?? this.isSuperuser,
    );
  }

  @override
  List<Object?> get props => [
        id,
        username,
        email,
        name,
        userRole,
        groups,
        permissions,
        isActive,
        isStaff,
        isSuperuser,
      ];

  @override
  String toString() {
    return 'BackendUserModel(id: $id, username: $username, email: $email, userRole: $userRole)';
  }
}
