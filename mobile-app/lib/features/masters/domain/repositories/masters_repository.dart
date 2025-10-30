import 'package:dartz/dartz.dart';
import '../../../../core/errors/failures.dart';
import '../entities/master_entity.dart';

/// Абстрактный репозиторий для работы с мастерами (Domain слой)
abstract class MastersRepository {
  /// Получить список всех мастеров
  Future<Either<Failure, List<MasterEntity>>> getMasters({
    int page = 1,
    int limit = 20,
    String? search,
    List<String>? specializations,
    String? location,
    double? minRating,
  });

  /// Получить мастера по ID
  Future<Either<Failure, MasterEntity>> getMasterById(String id);

  /// Поиск мастеров
  Future<Either<Failure, List<MasterEntity>>> searchMasters({
    required String query,
    int page = 1,
    int limit = 20,
    List<String>? specializations,
    String? location,
    double? minRating,
  });

  /// Получить мастеров по специализации
  Future<Either<Failure, List<MasterEntity>>> getMastersBySpecialization(
    String specialization, {
    int page = 1,
    int limit = 20,
  });

  /// Получить ближайших мастеров
  Future<Either<Failure, List<MasterEntity>>> getNearbyMasters({
    required double latitude,
    required double longitude,
    double radiusKm = 10.0,
    int limit = 20,
  });

  /// Добавить мастера в избранное
  Future<Either<Failure, Unit>> addToFavorites(String masterId);

  /// Удалить мастера из избранного
  Future<Either<Failure, Unit>> removeFromFavorites(String masterId);

  /// Получить избранных мастеров
  Future<Either<Failure, List<MasterEntity>>> getFavoriteMasters();

  /// Проверить, добавлен ли мастер в избранное
  Future<Either<Failure, bool>> isFavorite(String masterId);
}
