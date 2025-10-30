import 'dart:io';

/// Интерфейс для проверки состояния сети
abstract class NetworkInfo {
  Future<bool> get isConnected;
}

/// Реализация проверки состояния сети
class NetworkInfoImpl implements NetworkInfo {
  @override
  Future<bool> get isConnected async {
    try {
      final result = await InternetAddress.lookup('google.com');
      return result.isNotEmpty && result[0].rawAddress.isNotEmpty;
    } on SocketException catch (_) {
      return false;
    }
  }
}

/// Mock реализация для тестов
class NetworkInfoMock implements NetworkInfo {
  final bool isConnectedValue;
  
  const NetworkInfoMock(this.isConnectedValue);
  
  @override
  Future<bool> get isConnected async => isConnectedValue;
}
