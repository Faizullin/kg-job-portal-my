import 'home_data_source.dart';

/// Абстрактный репозиторий для home фичи
abstract class HomeRepository {
  // Здесь будут методы для работы с данными
  // Например: Future<Either<Failure, List<Service>>> getServices();
}

/// Реализация репозитория для home фичи
class HomeRepositoryImpl implements HomeRepository {
  final HomeDataSource _dataSource;
  
  const HomeRepositoryImpl({
    required HomeDataSource dataSource,
  }) : _dataSource = dataSource;
  
  // Здесь будет реализация методов
}
