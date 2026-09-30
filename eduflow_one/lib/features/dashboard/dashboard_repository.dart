import 'package:eduflow_core/eduflow_core.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../auth/session.dart';

final dashboardRepositoryProvider = Provider<DashboardRepository>((ref) {
  return DashboardRepository(ref.watch(dioClientProvider));
});

final dashboardProvider =
    FutureProvider.family<Map<String, dynamic>, EduFlowRole>((ref, role) async {
  return ref.watch(dashboardRepositoryProvider).load(role);
});

class DashboardRepository {
  DashboardRepository(this._client);
  final DioClient _client;

  Future<Map<String, dynamic>> load(EduFlowRole role) async {
    switch (role) {
      case EduFlowRole.student:
        return _data('/student/me/dashboard');
      case EduFlowRole.parent:
        return _data('/parent/dashboard');
      case EduFlowRole.management:
        return _data('/management/me/dashboard');
      case EduFlowRole.faculty:
        return _data('/faculty/me/dashboard');
      case EduFlowRole.unknown:
        throw StateError('Unsupported workspace');
    }
  }

  Future<Map<String, dynamic>> _data(String path) async {
    final response = await _client.dio.get(path);
    final body = Map<String, dynamic>.from(response.data as Map);
    return Map<String, dynamic>.from(body['data'] as Map? ?? body);
  }
}
