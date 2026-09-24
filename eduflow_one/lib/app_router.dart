import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'auth/session.dart';
import 'features/dashboard/role_dashboard_screen.dart';
import 'features/faculty/faculty_attendance_screen.dart';
import 'features/faculty/faculty_learners_screen.dart';
import 'features/faculty/faculty_leave_screen.dart';
import 'features/login/login_screen.dart';
import 'features/login/kevrin_launch_screen.dart';
import 'features/parent/parent_leave_screen.dart';
import 'features/parent/parent_notifications_screen.dart';
import 'features/student/student_notifications_screen.dart';
import 'features/management/management_leaves_screen.dart';
import 'features/management/management_timetable_screen.dart';
import 'features/management/management_workspace_screens.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/launch',
    routes: [
      GoRoute(path: '/launch', builder: (_, __) => const KevRynLaunchScreen()),
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(
          path: '/student',
          builder: (_, __) =>
              const RoleDashboardScreen(role: EduFlowRole.student)),
      GoRoute(path: '/student/notifications', builder: (_, __) => const StudentNotificationsScreen()),
      GoRoute(
          path: '/faculty',
          builder: (_, __) =>
              const RoleDashboardScreen(role: EduFlowRole.faculty)),
      GoRoute(
        path: '/faculty/attendance',
        builder: (_, state) => FacultyAttendanceScreen(
          classSlot: state.extra is Map
              ? Map<String, dynamic>.from(state.extra as Map)
              : const <String, dynamic>{},
        ),
      ),
      GoRoute(path: '/faculty/learners', builder: (_, __) => const FacultyLearnersScreen()),
      GoRoute(path: '/faculty/leave', builder: (_, __) => const FacultyLeaveScreen()),
      GoRoute(
          path: '/parent',
          builder: (_, __) =>
              const RoleDashboardScreen(role: EduFlowRole.parent)),
      GoRoute(path: '/parent/leave', builder: (_, __) => const ParentLeaveScreen()),
      GoRoute(path: '/parent/notifications', builder: (_, __) => const ParentNotificationsScreen()),
      GoRoute(
          path: '/management',
          builder: (_, __) =>
              const RoleDashboardScreen(role: EduFlowRole.management)),
      GoRoute(
        path: '/management/leaves',
        builder: (_, __) => const ManagementLeavesScreen(),
      ),
      GoRoute(path: '/management/operations', builder: (_, __) => const ManagementOperationsScreen()),
      GoRoute(path: '/management/people', builder: (_, __) => const ManagementPeopleScreen()),
      GoRoute(path: '/management/insights', builder: (_, __) => const ManagementInsightsScreen()),
      GoRoute(path: '/management/more', builder: (_, __) => const ManagementMoreScreen()),
      GoRoute(path: '/management/sms-log', builder: (_, __) => const ManagementSmsLogScreen()),
      GoRoute(path: '/management/timetable', builder: (_, __) => const ManagementTimetableScreen()),
    ],
    errorBuilder: (_, __) =>
        const Scaffold(body: Center(child: Text('This view is unavailable.'))),
  );
});

String routeForRole(EduFlowRole role) {
  switch (role) {
    case EduFlowRole.student:
      return '/student';
    case EduFlowRole.faculty:
      return '/faculty';
    case EduFlowRole.parent:
      return '/parent';
    case EduFlowRole.management:
      return '/management';
    case EduFlowRole.unknown:
      return '/login';
  }
}
