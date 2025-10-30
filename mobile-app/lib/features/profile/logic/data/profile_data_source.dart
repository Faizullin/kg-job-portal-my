import 'dart:async';
import '../../models/profile_model.dart';
import '../../models/edit_profile_request.dart';
import '../../models/edit_profile_response.dart';

/// Абстрактный источник данных для профиля
abstract class ProfileDataSource {
  /// Получение профиля пользователя
  Future<ProfileModel> getProfile();
  
  /// Обновление профиля пользователя
  Future<EditProfileResponse> updateProfile(EditProfileRequest request);
  
  /// Загрузка аватара
  Future<String> uploadAvatar(String imagePath);
  
  /// Удаление аккаунта
  Future<bool> deleteAccount();
}

/// Реализация источника данных для профиля
class ProfileDataSourceImpl implements ProfileDataSource {
  
  @override
  Future<ProfileModel> getProfile() async {
    // Имитация загрузки данных
    await Future.delayed(Duration(seconds: 1));
    
    // Возвращаем тестовые данные
    return ProfileModel(
      id: '1',
      name: 'Умар Исмаилов',
      email: 'umar.ismailov@gmail.com',
      phone: '+7 777 777 9999',
      city: 'Бишкек',
      gender: null,
      avatarUrl: null,
      createdAt: DateTime.now().subtract(Duration(days: 30)),
      updatedAt: DateTime.now(),
    );
  }
  
  @override
  Future<EditProfileResponse> updateProfile(EditProfileRequest request) async {
    // Имитация загрузки
    await Future.delayed(Duration(seconds: 2));
    
    // Валидация данных
    final errors = request.validate();
    if (errors.isNotEmpty) {
      return EditProfileResponse.error('Ошибка валидации: ${errors.values.first}');
    }
    
    try {
      // Объединяем имя и фамилию
      final fullName = '${request.firstName} ${request.lastName}'.trim();
      
      // Имитация успешного обновления
      final updatedProfile = ProfileModel(
        id: '1',
        name: fullName,
        email: request.email,
        phone: request.phone,
        city: request.city,
        gender: request.gender,
        avatarUrl: request.avatarUrl,
        createdAt: DateTime.now().subtract(Duration(days: 30)),
        updatedAt: DateTime.now(),
      );
      
      return EditProfileResponse.success(updatedProfile);
    } catch (e) {
      return EditProfileResponse.error('Ошибка обновления профиля: ${e.toString()}');
    }
  }
  
  @override
  Future<String> uploadAvatar(String imagePath) async {
    // Имитация загрузки аватара
    await Future.delayed(Duration(seconds: 3));
    
    // Возвращаем URL загруженного изображения
    return 'https://example.com/avatars/${DateTime.now().millisecondsSinceEpoch}.jpg';
  }
  
  @override
  Future<bool> deleteAccount() async {
    // Имитация удаления аккаунта
    await Future.delayed(Duration(seconds: 2));
    
    // Возвращаем успешный результат
    return true;
  }
}
