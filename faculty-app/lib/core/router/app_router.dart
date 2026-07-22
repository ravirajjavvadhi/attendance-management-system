import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/dashboard/presentation/screens/faculty_dashboard_screen.dart';
import '../../features/dashboard/presentation/screens/attendance_tracking_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/dashboard',
        name: 'dashboard',
        builder: (context, state) => const FacultyDashboardScreen(),
      ),
      GoRoute(
        path: '/attendance',
        name: 'attendance',
        builder: (context, state) {
          final extras = state.extra as Map<String, dynamic>? ?? {};
          return AttendanceTrackingScreen(
            sectionId: extras['sectionId']?.toString() ?? '',
            periodNumber: extras['periodNumber'] as int? ?? 1,
            subjectName: extras['subjectName']?.toString() ?? 'Subject',
            classDetails: extras['classDetails']?.toString() ?? 'Details',
            timeStr: extras['timeStr']?.toString() ?? 'Time',
            targetDate: extras['targetDate']?.toString() ?? DateTime.now().toIso8601String().split('T')[0],
          );
        },
      ),
    ],
  );
});
