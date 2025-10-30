# 🧩 ARCHITECTURE_GUIDE — интеграция с REST API

Ниже — адаптация шаблона чистой архитектуры под предоставленную схему эндпойнтов. Добавлены: маппинг доменов → фичи, контракты репозиториев/датасорсов, модели запросов/ответов, правила маршрутизации, обработка ошибок, пагинация/фильтры, загрузка файлов и WebSocket.

---

## 🗂️ Домены и фичи ↔️ эндпойнты

> Базовый префикс: `/api/v1`

| Домен/Фича | Эндпойнты |
|---|---|
| **Auth** | `POST /auth/firebase/`, `POST /auth/logout/` |
| **Core (справочники)** | `GET /core/app-versions/`, `/languages/`, `/service-areas/`, `/service-categories/`, `/service-subcategories/`, `/system-settings/` |
| **Chat** | `GET /chat/rooms/`, `GET/PUT/PATCH /chat/rooms/{id}/`, `POST /chat/rooms/create/`  ·  `GET /chat/messages/`, `GET/PUT/PATCH/DELETE /chat/messages/{id}/`, `POST /chat/messages/create/`  ·  `GET/DELETE /chat/attachments/{id}/`, `GET /chat/attachments/`, `POST /chat/attachments/create/`  ·  `GET /chat/websocket-info/` |
| **Users / Profile** | `GET/POST/PUT/PATCH/DELETE /profile/`  ·  `GET /users/`, `GET/PUT/PATCH /users/profile/`, `POST /users/profile/update/`  ·  Клиент: `GET/PUT/PATCH /users/client/`, `POST /users/client/update/`  ·  Провайдер: `GET/PUT/PATCH /users/provider/`, `POST /users/provider/update/`  ·  Списки: `GET /users/clients/`, `GET /users/providers/` |
| **Orders** | `GET /orders/`, `GET/PUT/PATCH /orders/{id}/`, `POST /orders/create/`  ·  Аукцион: `POST /orders/{order_id}/bids/`, `GET /orders/bids/`  ·  Споры: `POST /orders/{order_id}/disputes/`, `GET /orders/disputes/`, `GET/PUT/PATCH /orders/disputes/{id}/`  ·  Допы/фото: `GET /orders/addons/`, `GET /orders/photos/` |
| **Payments** | `GET /payments/`, `GET/PUT/PATCH /payments/{id}/`, `POST /payments/create/`  ·  Методы: `GET /payments/methods/`, `GET/PUT/PATCH/DELETE /payments/methods/{id}/`, `POST /payments/methods/create/`  ·  Инвойсы: `GET /payments/invoices/`, `GET /payments/invoices/{id}/`, `POST /payments/invoices/create/`  ·  Вебхуки: `GET /payments/webhooks/events/`, `POST /payments/webhooks/events/{event_id}/retry/`, `POST /payments/webhooks/stripe/drf/` |
| **Notifications** | `GET /notifications/`, `GET/PUT/PATCH /notifications/{id}/`, `POST /notifications/create/`  ·  Настройки: `GET/PUT/PATCH /notifications/settings/`  ·  Шаблоны: `GET /notifications/templates/`, `GET/PUT/PATCH /notifications/templates/{id}/`, `POST /notifications/templates/create/` |
| **Reviews** | `GET/POST /reviews/`, `GET/PUT/PATCH/DELETE /reviews/{id}/`  ·  `GET /reviews/analytics/`  ·  По связям: `GET /reviews/order/{order_id}/`, `GET /reviews/provider/{provider_id}/` |
| **Search** | `GET /search/global/`, `GET /search/orders/`, `GET /search/providers/` |
| **Analytics** | `GET /analytics/dashboard/`, `/activities/` (+`POST /analytics/activities/create/`), `/business/` (+`POST /business/create/`), `/categories/` (+`POST /categories/create/`), `/orders/` (+`POST /orders/create/`), `/performance/` |

> Для `v1` вне префикса (`GET /api/schema/`, `GET /api/v1/...`) держим общий клиент и перехватчики.

---

## 🏗️ Структура фичи (пример: Orders)

```
lib/features/orders/
  logic/
    bloc/
      orders_bloc.dart
    data/
      datasources/
        orders_remote_ds.dart
      models/
        order_model.dart
        order_request.dart
      repositories/
        orders_repository_impl.dart
    domain/
      entities/
        order_entity.dart
      repositories/
        orders_repository.dart
      usecases/
        fetch_orders.dart
  screens/
    orders_screen.dart
  widgets/
    order_tile.dart
```

---

## 🔌 Конфигурация HTTP клиента и роуты API

```dart
// lib/core/network/api_routes.dart
class ApiRoutes {
  static const base = '/api/v1';
  // Auth
  static const authFirebase = '$base/auth/firebase/';
  static const authLogout = '$base/auth/logout/';
  // Chat
  static const chatRooms = '$base/chat/rooms/';
  static String chatRoom(int id) => '$base/chat/rooms/$id/';
  static const chatRoomsCreate = '$base/chat/rooms/create/';
  static const chatMessages = '$base/chat/messages/';
  static String chatMessage(int id) => '$base/chat/messages/$id/';
  static const chatMessagesCreate = '$base/chat/messages/create/';
  static const chatAttachments = '$base/chat/attachments/';
  static String chatAttachment(int id) => '$base/chat/attachments/$id/';
  static const chatAttachmentsCreate = '$base/chat/attachments/create/';
  static const chatWebSocketInfo = '$base/chat/websocket-info/';
  // Users
  static const profile = '$base/profile/';
  static const users = '$base/users/';
  static const usersProfile = '$base/users/profile/';
  static const usersProfileUpdate = '$base/users/profile/update/';
  static const usersClient = '$base/users/client/';
  static const usersClientUpdate = '$base/users/client/update/';
  static const usersClients = '$base/users/clients/';
  static const usersProvider = '$base/users/provider/';
  static const usersProviderUpdate = '$base/users/provider/update/';
  static const usersProviders = '$base/users/providers/';
  // Orders
  static const orders = '$base/orders/';
  static String order(int id) => '$base/orders/$id/';
  static const ordersCreate = '$base/orders/create/';
  static String orderBids(int orderId) => '$base/orders/$orderId/bids/';
  static String orderDisputes(int orderId) => '$base/orders/$orderId/disputes/';
  static const ordersBids = '$base/orders/bids/';
  static const ordersDisputes = '$base/orders/disputes/';
  static String ordersDispute(int id) => '$base/orders/disputes/$id/';
  static const ordersAddons = '$base/orders/addons/';
  static const ordersPhotos = '$base/orders/photos/';
  // Payments
  static const payments = '$base/payments/';
  static String payment(int id) => '$base/payments/$id/';
  static const paymentsCreate = '$base/payments/create/';
  static const paymentMethods = '$base/payments/methods/';
  static String paymentMethod(int id) => '$base/payments/methods/$id/';
  static const paymentMethodsCreate = '$base/payments/methods/create/';
  static const invoices = '$base/payments/invoices/';
  static String invoice(int id) => '$base/payments/invoices/$id/';
  static const invoicesCreate = '$base/payments/invoices/create/';
  static const webhookEvents = '$base/payments/webhooks/events/';
  static String webhookRetry(String eventId) => '$base/payments/webhooks/events/$eventId/retry/';
  static const webhookStripeDrf = '$base/payments/webhooks/stripe/drf/';
  // Notifications
  static const notifications = '$base/notifications/';
  static String notification(int id) => '$base/notifications/$id/';
  static const notificationsCreate = '$base/notifications/create/';
  static const notificationSettings = '$base/notifications/settings/';
  static const notificationTemplates = '$base/notifications/templates/';
  static String notificationTemplate(int id) => '$base/notifications/templates/$id/';
  static const notificationTemplatesCreate = '$base/notifications/templates/create/';
  // Reviews
  static const reviews = '$base/reviews/';
  static String review(int id) => '$base/reviews/$id/';
  static const reviewsAnalytics = '$base/reviews/analytics/';
  static String reviewsByOrder(int orderId) => '$base/reviews/order/$orderId/';
  static String reviewsByProvider(int providerId) => '$base/reviews/provider/$providerId/';
  // Search
  static const searchGlobal = '$base/search/global/';
  static const searchOrders = '$base/search/orders/';
  static const searchProviders = '$base/search/providers/';
  // Analytics
  static const analyticsDashboard = '$base/analytics/dashboard/';
  static const analyticsActivities = '$base/analytics/activities/';
  static const analyticsActivitiesCreate = '$base/analytics/activities/create/';
  static const analyticsBusiness = '$base/analytics/business/';
  static const analyticsBusinessCreate = '$base/analytics/business/create/';
  static const analyticsCategories = '$base/analytics/categories/';
  static const analyticsCategoriesCreate = '$base/analytics/categories/create/';
  static const analyticsOrders = '$base/analytics/orders/';
  static const analyticsOrdersCreate = '$base/analytics/orders/create/';
  static const analyticsPerformance = '$base/analytics/performance/';
  // Core
  static const coreAppVersions = '$base/core/app-versions/';
  static const coreLanguages = '$base/core/languages/';
  static const coreServiceAreas = '$base/core/service-areas/';
  static const coreServiceCategories = '$base/core/service-categories/';
  static const coreServiceSubcategories = '$base/core/service-subcategories/';
  static const coreSystemSettings = '$base/core/system-settings/';
}
```

```dart
// lib/core/network/http_client.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class HttpClient {
  HttpClient(this._baseUrl, {this.getToken});

  final String _baseUrl;
  final Future<String?> Function()? getToken;

  Future<http.Response> _send(String method, String path, {Map<String, String>? headers, Object? body, Map<String, String>? query}) async {
    final uri = Uri.parse('$_baseUrl$path').replace(queryParameters: query);
    final token = await getToken?.call();
    final h = {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
      ...?headers,
    };
    switch (method) {
      case 'GET': return http.get(uri, headers: h);
      case 'POST': return http.post(uri, headers: h, body: body);
      case 'PUT': return http.put(uri, headers: h, body: body);
      case 'PATCH': return http.patch(uri, headers: h, body: body);
      case 'DELETE': return http.delete(uri, headers: h);
      default: throw UnsupportedError('Method $method');
    }
  }

  Future<Map<String, dynamic>> getJson(String path, {Map<String, String>? query}) async {
    final res = await _send('GET', path, query: query);
    return _parse(res);
  }
  Future<Map<String, dynamic>> postJson(String path, Map<String, dynamic> data) async {
    final res = await _send('POST', path, body: jsonEncode(data));
    return _parse(res);
  }
  Future<Map<String, dynamic>> putJson(String path, Map<String, dynamic> data) async {
    final res = await _send('PUT', path, body: jsonEncode(data));
    return _parse(res);
  }
  Future<Map<String, dynamic>> patchJson(String path, Map<String, dynamic> data) async {
    final res = await _send('PATCH', path, body: jsonEncode(data));
    return _parse(res);
  }
  Future<void> delete(String path) async {
    final res = await _send('DELETE', path);
    _parse(res);
  }

  Map<String, dynamic> _parse(http.Response res) {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      return res.body.isNotEmpty ? jsonDecode(res.body) as Map<String, dynamic> : <String, dynamic>{};
    }
    throw ApiException(status: res.statusCode, body: res.body);
  }
}

class ApiException implements Exception {
  ApiException({required this.status, this.body});
  final int status;
  final String? body;
  @override
  String toString() => 'ApiException($status): $body';
}
```

---

## 🔐 Auth: Firebase вход и Logout

```dart
// lib/features/auth/logic/data/datasources/auth_remote_ds.dart
class AuthRemoteDataSource {
  final HttpClient client;
  AuthRemoteDataSource(this.client);

  Future<AuthResponse> signInWithFirebase(String idToken) async {
    final json = await client.postJson(ApiRoutes.authFirebase, {'id_token': idToken});
    return AuthResponse.fromJson(json);
  }

  Future<void> logout() => client.postJson(ApiRoutes.authLogout, {});
}

class AuthResponse {
  final String accessToken; // jwt
  final String refreshToken;
  AuthResponse({required this.accessToken, required this.refreshToken});
  factory AuthResponse.fromJson(Map<String, dynamic> j) => AuthResponse(
    accessToken: j['access'] as String,
    refreshToken: j['refresh'] as String,
  );
}
```

---

## 💬 Chat: сообщения, вложения, WebSocket

```dart
// models
class ChatMessage {
  final int id;
  final int roomId;
  final int authorId;
  final String text;
  final DateTime createdAt;
  ChatMessage({required this.id, required this.roomId, required this.authorId, required this.text, required this.createdAt});
  factory ChatMessage.fromJson(Map<String, dynamic> j) => ChatMessage(
    id: j['id'], roomId: j['room_id'], authorId: j['author_id'], text: j['text'], createdAt: DateTime.parse(j['created_at']),
  );
}

class UploadAttachmentRequest { // для POST /chat/attachments/create/
  final String filePath; // локальный путь
  final String? caption;
  const UploadAttachmentRequest({required this.filePath, this.caption});
}
```

```dart
// datasource (multipart пример)
import 'package:http/http.dart' as http;

class ChatRemoteDataSource {
  final HttpClient client;
  final String base;
  ChatRemoteDataSource(this.client, this.base);

  Future<List<ChatMessage>> getMessages({int? roomId, int page = 1}) async {
    final json = await client.getJson(ApiRoutes.chatMessages, query: {
      if (roomId != null) 'room_id': '$roomId',
      'page': '$page',
    });
    final list = (json['results'] as List).cast<Map<String, dynamic>>();
    return list.map(ChatMessage.fromJson).toList();
  }

  Future<void> deleteAttachment(int id) => client.delete(ApiRoutes.chatAttachment(id));
}
```

> WebSocket: получаем URL и токен через `GET /chat/websocket-info/`, далее подключаемся в UI слое (например, через `web_socket_channel`), события транслируем в BLoC.

---

## 👤 Users & Profile

```dart
class UserProfile {
  final int id; final String name; final String email; final String role; // client|provider|admin
  UserProfile({required this.id, required this.name, required this.email, required this.role});
  factory UserProfile.fromJson(Map<String, dynamic> j) => UserProfile(
    id: j['id'], name: j['name'], email: j['email'], role: j['role'],
  );
}

abstract class UsersRepository {
  Future<UserProfile> getMe();
  Future<UserProfile> updateMe(Map<String, dynamic> patch);
  Future<List<UserProfile>> listClients({int page = 1});
  Future<List<UserProfile>> listProviders({int page = 1});
}
```

---

## 📦 Orders: контракт, модели, репозиторий

```dart
class OrderEntity {
  final int id; final String status; final double total; final int clientId; final int? providerId; final DateTime createdAt;
  OrderEntity({required this.id, required this.status, required this.total, required this.clientId, this.providerId, required this.createdAt});
  factory OrderEntity.fromJson(Map<String, dynamic> j) => OrderEntity(
    id: j['id'], status: j['status'], total: (j['total'] as num).toDouble(), clientId: j['client_id'], providerId: j['provider_id'], createdAt: DateTime.parse(j['created_at']),
  );
}

class CreateOrderRequest { // POST /orders/create/
  final String title; final String description; final int categoryId; final double budget;
  const CreateOrderRequest({required this.title, required this.description, required this.categoryId, required this.budget});
  Map<String, dynamic> toJson() => {
    'title': title,
    'description': description,
    'category_id': categoryId,
    'budget': budget,
  };
}

abstract class OrdersRepository {
  Future<List<OrderEntity>> list({int page = 1});
  Future<OrderEntity> get(int id);
  Future<OrderEntity> create(CreateOrderRequest req);
  Future<OrderEntity> update(int id, Map<String, dynamic> patch);
  Future<void> bid(int orderId, Map<String, dynamic> data); // POST /orders/{id}/bids/
  Future<void> dispute(int orderId, Map<String, dynamic> data); // POST /orders/{id}/disputes/
}
```

---

## 💳 Payments: методы, инвойсы, события вебхуков

```dart
class PaymentMethod { final int id; final String brand; final String last4; final bool isDefault; /* ... */
  PaymentMethod({required this.id, required this.brand, required this.last4, required this.isDefault});
  factory PaymentMethod.fromJson(Map<String, dynamic> j) => PaymentMethod(
    id: j['id'], brand: j['brand'], last4: j['last4'], isDefault: j['is_default'] ?? false,
  );
}

abstract class PaymentsRepository {
  Future<List<PaymentMethod>> methods();
  Future<PaymentMethod> addMethod(Map<String, dynamic> tokenized); // POST /payments/methods/create/
  Future<void> removeMethod(int id);
  Future<List<Invoice>> invoices();
  Future<Invoice> createInvoice(Map<String, dynamic> payload);
}
```

---

## 🔔 Notifications: лента, настройки, шаблоны

```dart
class NotificationItem { final int id; final String type; final String title; final String? body; final bool read; final DateTime createdAt; /* ... */
  NotificationItem({required this.id, required this.type, required this.title, this.body, required this.read, required this.createdAt});
  factory NotificationItem.fromJson(Map<String, dynamic> j) => NotificationItem(
    id: j['id'], type: j['type'], title: j['title'], body: j['body'], read: j['read'] ?? false, createdAt: DateTime.parse(j['created_at']),
  );
}

abstract class NotificationsRepository {
  Future<List<NotificationItem>> list({int page = 1});
  Future<NotificationItem> update(int id, Map<String, dynamic> patch); // read:true, etc
  Future<Map<String, dynamic>> settings();
  Future<Map<String, dynamic>> updateSettings(Map<String, dynamic> patch);
}
```

---

## ⭐ Reviews & Analytics

```dart
abstract class ReviewsRepository {
  Future<List<Review>> list({int? orderId, int? providerId, int page = 1});
  Future<Review> create(Map<String, dynamic> payload);
  Future<Review> update(int id, Map<String, dynamic> patch);
  Future<void> delete(int id);
  Future<Map<String, dynamic>> analytics();
}

abstract class AnalyticsRepository {
  Future<Map<String, dynamic>> dashboard();
  Future<List<Map<String, dynamic>>> activities();
  Future<void> addActivity(Map<String, dynamic> payload);
  Future<Map<String, dynamic>> business();
  Future<void> addBusinessMetric(Map<String, dynamic> payload);
  /* categories, orders, performance — аналогично */
}
```

---

## 🧱 BLoC паттерн: пример (Orders)

```dart
// events
sealed class OrdersEvent {}
class OrdersFetched extends OrdersEvent { final int page; OrdersFetched({this.page = 1}); }
class OrderCreated extends OrdersEvent { final CreateOrderRequest req; OrderCreated(this.req); }
class OrderPatched extends OrdersEvent { final int id; final Map<String, dynamic> patch; OrderPatched(this.id, this.patch); }

// states
sealed class OrdersState { const OrdersState(); }
class OrdersInitial extends OrdersState { const OrdersInitial(); }
class OrdersLoading extends OrdersState { const OrdersLoading(); }
class OrdersLoaded extends OrdersState { final List<OrderEntity> items; final int page; const OrdersLoaded(this.items, this.page); }
class OrdersError extends OrdersState { final String message; const OrdersError(this.message); }

// bloc
class OrdersBloc extends Bloc<OrdersEvent, OrdersState> {
  final OrdersRepository repo;
  OrdersBloc(this.repo) : super(const OrdersInitial()) {
    on<OrdersFetched>(_onFetched);
    on<OrderCreated>(_onCreated);
    on<OrderPatched>(_onPatched);
  }
  Future<void> _onFetched(OrdersFetched e, Emitter<OrdersState> emit) async {
    emit(const OrdersLoading());
    try { final items = await repo.list(page: e.page); emit(OrdersLoaded(items, e.page)); }
    catch (err) { emit(OrdersError(err.toString())); }
  }
  Future<void> _onCreated(OrderCreated e, Emitter<OrdersState> emit) async {
    try { await repo.create(e.req); add(OrdersFetched()); }
    catch (err) { emit(OrdersError(err.toString())); }
  }
  Future<void> _onPatched(OrderPatched e, Emitter<OrdersState> emit) async {
    try { await repo.update(e.id, e.patch); add(OrdersFetched()); }
    catch (err) { emit(OrdersError(err.toString())); }
  }
}
```

---

## ⚖️ Роли и доступ (набросок матрицы)

| Фича → Роль | Гость | Клиент | Провайдер | Админ |
|---|---:|---:|---:|---:|
| Auth (firebase) | ✅ | ✅ | ✅ | ✅ |
| Profile | ⛔ | R/W (своё) | R/W (своё) | R/W (любое) |
| Users (lists) | ⛔ | R (providers) | R (clients) | R/W (все) |
| Chat | ⛔ | R/W в своих комнатах | R/W в своих комнатах | R/W (все) |
| Orders | ⛔ | Create/Read свои, Dispute свои | Bid, Read назначенные | R/W (все) |
| Payments | ⛔ | Методы/инвойсы свои | Методы/инвойсы свои | R/W (все) |
| Notifications | ⛔ | свои | свои | все |
| Reviews | ⛔ | Create для заказов клиента | Create для заказов провайдера | R/W (все) |
| Search | ⛔ | ограничено контекстом | ограничено контекстом | все |
| Analytics | ⛔ | агрегаты личные | агрегаты личные | агрегаты глобальные |

---

## 🔎 Пагинация и фильтры
- Общие параметры: `page`, `page_size`, доменные фильтры (например, `status`, `room_id`, `provider_id`).
- В `HttpClient.getJson(..., query: {...})` передавать только непустые.
- Ответы-коллекции приводить к унифицированной модели.

---

## 🖼️ Загрузка файлов (chat attachments)
- Для `POST /chat/attachments/create/` используйте `http.MultipartRequest` на уровне отдельного uploader.
- При `DELETE /chat/attachments/{id}/` — синхронизируйте локальный кэш.

---

## 🌐 WebSocket (chat)
- `GET /chat/websocket-info/` → `{ url, token }`.
- Реконнект, буфер непрочитанных, баджи.

---

## 🧪 Тестирование и обработка ошибок (guard)
См. примеры в тексте. Используйте `mockito`, `bloc_test`, доменные ошибки и маппинг HTTP-кодов.
