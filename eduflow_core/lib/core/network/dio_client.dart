import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../auth/auth_service.dart';

class DioClient {
  final Dio _dio;
  final AuthService _authService;

  DioClient(this._dio, this._authService) {
    _dio.options.baseUrl = 'https://attendance-management-system-afk0.onrender.com/api/v1';
    _dio.options.connectTimeout = const Duration(seconds: 60);
    _dio.options.receiveTimeout = const Duration(seconds: 60);
    _dio.options.sendTimeout = const Duration(seconds: 60);

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          final token = _authService.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (DioException e, handler) async {
          // Handle 401 Unauthorized -> Refresh Token Flow
          if (e.response?.statusCode == 401) {
            // Logic to call refresh token API, save new token, and retry the request
            // For now, pass the error
          }
          return handler.next(e);
        },
      ),
    );
  }

  Dio get dio => _dio;
}

final dioClientProvider = Provider<DioClient>((ref) {
  final authService = ref.watch(authServiceProvider);
  return DioClient(Dio(), authService);
});
