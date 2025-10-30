import 'dart:async';
import 'package:dartz/dartz.dart';
import '../../models/master_model.dart';
import '../../models/service_category_model.dart';
import '../../models/masters_search_request.dart';
import '../../models/masters_search_response.dart';
import 'masters_data_source.dart';

/// Абстрактный репозиторий для мастеров
abstract class MastersRepository {
  /// Получение списка мастеров
  Future<Either<String, MastersSearchResponse>> getMasters(MastersSearchRequest request);
  
  /// Получение категорий услуг
  Future<Either<String, List<ServiceCategoryModel>>> getServiceCategories();
  
  /// Получение статистики мастеров
  Future<Either<String, Map<String, dynamic>>> getMastersStats();
  
  /// Получение конкретного мастера по ID
  Future<Either<String, MasterModel>> getMasterById(String masterId);
}

/// Реализация репозитория для мастеров
class MastersRepositoryImpl implements MastersRepository {
  final MastersDataSource _dataSource;
  
  MastersRepositoryImpl({
    required MastersDataSource dataSource,
  }) : _dataSource = dataSource;
  
  @override
  Future<Either<String, MastersSearchResponse>> getMasters(MastersSearchRequest request) async {
    try {
      final response = await _dataSource.getMasters(request);
      
      // Проверяем, есть ли ошибка в ответе
      if (response.nextPageToken != null && response.nextPageToken!.startsWith('Ошибка')) {
        return Left(response.nextPageToken!);
      }
      
      return Right(response);
    } catch (e) {
      return Left('Ошибка загрузки мастеров: ${e.toString()}');
    }
  }
  
  @override
  Future<Either<String, List<ServiceCategoryModel>>> getServiceCategories() async {
    try {
      final categories = await _dataSource.getServiceCategories();
      return Right(categories);
    } catch (e) {
      return Left('Ошибка загрузки категорий услуг: ${e.toString()}');
    }
  }
  
  @override
  Future<Either<String, Map<String, dynamic>>> getMastersStats() async {
    try {
      final stats = await _dataSource.getMastersStats();
      return Right(stats);
    } catch (e) {
      return Left('Ошибка загрузки статистики: ${e.toString()}');
    }
  }
  
  @override
  Future<Either<String, MasterModel>> getMasterById(String masterId) async {
    try {
      final master = await _dataSource.getMasterById(masterId);
      return Right(master);
    } catch (e) {
      return Left('Ошибка загрузки мастера: ${e.toString()}');
    }
  }
}
