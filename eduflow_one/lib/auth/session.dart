import 'dart:convert';

import 'package:eduflow_core/eduflow_core.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

enum EduFlowRole { parent, faculty, student, management, unknown }

class UserSession {
  const UserSession(
      {required this.token, required this.role, required this.tenantId});

  final String token;
  final EduFlowRole role;
  final int? tenantId;

  static UserSession? fromToken(String? token) {
    if (token == null || token.isEmpty) return null;
    try {
      final parts = token.split('.');
      if (parts.length != 3) return null;
      final payload = jsonDecode(
        utf8.decode(base64Url.decode(base64Url.normalize(parts[1]))),
      ) as Map<String, dynamic>;
      return UserSession(
        token: token,
        role: _roleFromValue(payload['role']?.toString()),
        tenantId: int.tryParse(payload['tenant_id']?.toString() ?? ''),
      );
    } catch (_) {
      return null;
    }
  }

  static EduFlowRole _roleFromValue(String? value) {
    switch (value) {
      case 'PARENT':
        return EduFlowRole.parent;
      case 'FACULTY':
        return EduFlowRole.faculty;
      case 'STUDENT':
        return EduFlowRole.student;
      case 'MANAGEMENT':
      case 'ADMIN':
      case 'SUPERADMIN':
        return EduFlowRole.management;
      default:
        return EduFlowRole.unknown;
    }
  }
}

final sessionProvider = StateProvider<UserSession?>((ref) {
  return UserSession.fromToken(ref.watch(authServiceProvider).getToken());
});

Future<void> saveSession(WidgetRef ref, String token) async {
  final session = UserSession.fromToken(token);
  if (session == null || session.role == EduFlowRole.unknown) {
    throw const FormatException(
        'The server returned an account without a supported role.');
  }
  await ref.read(authServiceProvider).saveToken(token);
  ref.read(sessionProvider.notifier).state = session;
}

Future<void> clearSession(WidgetRef ref) async {
  await ref.read(authServiceProvider).clearSession();
  ref.read(sessionProvider.notifier).state = null;
}
