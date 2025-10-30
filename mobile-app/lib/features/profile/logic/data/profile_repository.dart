import 'dart:async';
import 'package:dartz/dartz.dart';
import '../../models/profile_model.dart';
import '../../models/edit_profile_request.dart';
import '../../models/edit_profile_response.dart';
import 'profile_data_source.dart';

/// Абстрактный репозиторий для профиля
abstract class ProfileRepository {
  /// Получение профиля пользователя
  Future<Either<String, ProfileModel>> getProfile();
  
  /// Обновление профиля пользователя
  Future<Either<String, EditProfileResponse>> updateProfile(EditProfileRequest request);
  
  /// Загрузка аватара
  Future<Either<String, String>> uploadAvatar(String imagePath);
  
  /// Удаление аккаунта
  Future<Either<String, bool>> deleteAccount();
}

/// Реализация репозитория для профиля
class ProfileRepositoryImpl implements ProfileRepository {
  final ProfileDataSource _dataSource;
  
  ProfileRepositoryImpl({
    required ProfileDataSource dataSource,
  }) : _dataSource = dataSource;
  
  @override
  Future<Either<String, ProfileModel>> getProfile() async {
    try {
      final profile = await _dataSource.getProfile();
      return Right(profile);
    } catch (e) {
      return Left('Ошибка загрузки профиля: ${e.toString()}');
    }
  }
  
  @override
  Future<Either<String, EditProfileResponse>> updateProfile(EditProfileRequest request) async {
    try {
      final response = await _dataSource.updateProfile(request);
      
      if (response.success) {
        return Right(response);
      } else {
        return Left(response.message);
      }
    } catch (e) {
      return Left('Ошибка обновления профиля: ${e.toString()}');
    }
  }
  
  @override
  Future<Either<String, String>> uploadAvatar(String imagePath) async {
    try {
      final avatarUrl = await _dataSource.uploadAvatar(imagePath);
      return Right(avatarUrl);
    } catch (e) {
      return Left('Ошибка загрузки аватара: ${e.toString()}');
    }
  }
  
  @override
  Future<Either<String, bool>> deleteAccount() async {
    try {
      final result = await _dataSource.deleteAccount();
      return Right(result);
    } catch (e) {
      return Left('Ошибка удаления аккаунта: ${e.toString()}');
    }
  }
}
