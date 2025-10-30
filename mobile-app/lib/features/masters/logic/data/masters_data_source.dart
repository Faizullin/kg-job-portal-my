import 'dart:async';
import '../../models/master_model.dart';
import '../../models/service_category_model.dart';
import '../../models/masters_search_request.dart';
import '../../models/masters_search_response.dart';

/// Абстрактный источник данных для мастеров
abstract class MastersDataSource {
  /// Получение списка мастеров
  Future<MastersSearchResponse> getMasters(MastersSearchRequest request);
  
  /// Получение категорий услуг
  Future<List<ServiceCategoryModel>> getServiceCategories();
  
  /// Получение статистики мастеров
  Future<Map<String, dynamic>> getMastersStats();
  
  /// Получение конкретного мастера по ID
  Future<MasterModel> getMasterById(String masterId);
}

/// Реализация источника данных для мастеров
class MastersDataSourceImpl implements MastersDataSource {
  
  @override
  Future<MastersSearchResponse> getMasters(MastersSearchRequest request) async {
    // Имитация загрузки данных
    await Future.delayed(Duration(milliseconds: 800));
    
    // Валидация запроса
    final errors = request.validate();
    if (errors.isNotEmpty) {
      return MastersSearchResponse.error(errors.values.first);
    }
    
    try {
      // Имитация получения данных с сервера
      final masters = _generateMockMasters(request);
      
      return MastersSearchResponse(
        masters: masters,
        totalCount: 127,
        currentPage: request.page,
        totalPages: 7,
        hasMore: request.page < 7,
      );
    } catch (e) {
      return MastersSearchResponse.error('Ошибка загрузки мастеров: ${e.toString()}');
    }
  }
  
  @override
  Future<List<ServiceCategoryModel>> getServiceCategories() async {
    // Имитация загрузки
    await Future.delayed(Duration(milliseconds: 500));
    
    return [
      ServiceCategoryModel(
        id: '1',
        title: 'Сантехника',
        imageUrl: 'https://picsum.photos/seed/722/600',
        backgroundColor: '0xFFE6F3FF',
        isActive: true,
        masterCount: 15,
        createdAt: DateTime.now().subtract(Duration(days: 30)),
      ),
      ServiceCategoryModel(
        id: '2',
        title: 'Электрика',
        imageUrl: 'https://picsum.photos/seed/723/600',
        backgroundColor: '0xFFFFE6CC',
        isActive: true,
        masterCount: 12,
        createdAt: DateTime.now().subtract(Duration(days: 30)),
      ),
      ServiceCategoryModel(
        id: '3',
        title: 'Мебель',
        imageUrl: 'https://picsum.photos/seed/724/600',
        backgroundColor: '0xFFFFE6F0',
        isActive: true,
        masterCount: 8,
        createdAt: DateTime.now().subtract(Duration(days: 30)),
      ),
      ServiceCategoryModel(
        id: '4',
        title: 'Отделочные работы',
        imageUrl: 'https://picsum.photos/seed/725/600',
        backgroundColor: '0xFFE6E6FF',
        isActive: true,
        masterCount: 20,
        createdAt: DateTime.now().subtract(Duration(days: 30)),
      ),
      ServiceCategoryModel(
        id: '5',
        title: 'Общие работы',
        imageUrl: 'https://picsum.photos/seed/726/600',
        backgroundColor: '0xFFE6FFE6',
        isActive: true,
        masterCount: 25,
        createdAt: DateTime.now().subtract(Duration(days: 30)),
      ),
      ServiceCategoryModel(
        id: '6',
        title: 'Уборка',
        imageUrl: 'https://picsum.photos/seed/727/600',
        backgroundColor: '0xFFFFE6CC',
        isActive: true,
        masterCount: 18,
        createdAt: DateTime.now().subtract(Duration(days: 30)),
      ),
    ];
  }
  
  @override
  Future<Map<String, dynamic>> getMastersStats() async {
    // Имитация загрузки
    await Future.delayed(Duration(milliseconds: 300));
    
    return {
      'total_masters': 127,
      'average_rating': 4.8,
      'average_response_time': '2ч',
      'online_masters': 45,
      'total_completed_jobs': 2847,
    };
  }
  
  @override
  Future<MasterModel> getMasterById(String masterId) async {
    // Имитация загрузки
    await Future.delayed(Duration(milliseconds: 600));
    
    // Возвращаем тестового мастера
    return MasterModel(
      id: masterId,
      name: 'Мамут Рахал',
      specialty: 'Сборка мебели',
      rating: 4.8,
      reviewCount: 127,
      location: 'Бишкек, Свердловский район',
      isOnline: true,
      completedJobs: 89,
      hourlyRate: '800 ₸',
      responseTime: 'Отвечает за 2 часа',
      skills: ['Сборка мебели', 'Ремонт мебели', 'Установка техники'],
      portfolioImages: [
        'https://picsum.photos/seed/994/600',
        'https://picsum.photos/seed/995/600',
        'https://picsum.photos/seed/996/600',
      ],
      avatarUrl: 'https://picsum.photos/seed/56/600',
      createdAt: DateTime.now().subtract(Duration(days: 180)),
      updatedAt: DateTime.now(),
    );
  }
  
  /// Генерация тестовых мастеров
  List<MasterModel> _generateMockMasters(MastersSearchRequest request) {
    final masters = <MasterModel>[];
    final specialties = ['Сантехник', 'Электрик', 'Мебельщик', 'Отделочник', 'Уборщик'];
    
    for (int i = 0; i < 20; i++) {
      final specialty = specialties[i % specialties.length];
      masters.add(MasterModel(
        id: 'master_$i',
        name: 'Мастер ${i + 1}',
        specialty: specialty,
        rating: 3.5 + (i % 15) * 0.1,
        reviewCount: 10 + (i % 50),
        location: 'Бишкек, Район ${i % 4 + 1}',
        isOnline: i % 3 == 0,
        completedJobs: 20 + (i % 100),
        hourlyRate: '${500 + (i % 500)} ₸',
        responseTime: i % 2 == 0 ? 'Отвечает за 1 час' : 'Отвечает за 2 часа',
        skills: ['$specialty', 'Ремонт', 'Консультация'],
        portfolioImages: [
          'https://picsum.photos/seed/${900 + i}/600',
          'https://picsum.photos/seed/${910 + i}/600',
        ],
        avatarUrl: 'https://picsum.photos/seed/${100 + i}/600',
        createdAt: DateTime.now().subtract(Duration(days: 100 + i)),
        updatedAt: DateTime.now().subtract(Duration(days: i)),
      ));
    }
    
    // Применяем фильтры
    if (request.query != null && request.query!.isNotEmpty) {
      masters.retainWhere((master) =>
          master.name.toLowerCase().contains(request.query!.toLowerCase()) ||
          master.specialty.toLowerCase().contains(request.query!.toLowerCase()));
    }
    
    if (request.minRating != null) {
      masters.retainWhere((master) => master.rating >= request.minRating!);
    }
    
    if (request.isOnline != null) {
      masters.retainWhere((master) => master.isOnline == request.isOnline);
    }
    
    // Сортировка
    switch (request.sortBy) {
      case 'rating':
        masters.sort((a, b) => b.rating.compareTo(a.rating));
        break;
      case 'price':
        masters.sort((a, b) {
          final aPrice = int.tryParse(a.hourlyRate.replaceAll(RegExp(r'[^\d]'), '')) ?? 0;
          final bPrice = int.tryParse(b.hourlyRate.replaceAll(RegExp(r'[^\d]'), '')) ?? 0;
          return aPrice.compareTo(bPrice);
        });
        break;
      default:
        // По умолчанию сортируем по рейтингу
        masters.sort((a, b) => b.rating.compareTo(a.rating));
    }
    
    return masters;
  }
}
