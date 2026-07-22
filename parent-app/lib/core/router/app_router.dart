import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/otp_screen.dart';
import '../../features/home/presentation/screens/home_dashboard_screen.dart';
import '../../features/home/presentation/screens/settings_screen.dart';
import '../../features/home/presentation/screens/documents_screen.dart';
import '../../features/notifications/presentation/screens/notification_center_screen.dart';
import '../../features/home/presentation/screens/leave_request_screen.dart';
import '../../features/home/presentation/screens/contact_faculty_screen.dart';
import '../../features/home/presentation/screens/fee_payment_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/otp/:mobile',
        name: 'otp',
        builder: (context, state) {
          final mobile = state.pathParameters['mobile']!;
          return OtpScreen(mobileNumber: mobile);
        },
      ),
      GoRoute(
        path: '/home',
        name: 'home',
        builder: (context, state) => const HomeDashboardScreen(),
      ),
      GoRoute(
        path: '/settings',
        name: 'settings',
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/notifications',
        name: 'notifications',
        builder: (context, state) => const NotificationCenterScreen(),
      ),
      GoRoute(
        path: '/documents',
        name: 'documents',
        builder: (context, state) => const DocumentsScreen(),
      ),
      GoRoute(
        path: '/leave-request',
        name: 'leave_request',
        builder: (context, state) => const LeaveRequestScreen(),
      ),
      GoRoute(
        path: '/contact-faculty',
        name: 'contact_faculty',
        builder: (context, state) => const ContactFacultyScreen(),
      ),
      GoRoute(
        path: '/pay-fees',
        name: 'pay_fees',
        builder: (context, state) => const FeePaymentScreen(),
      ),
    ],
  );
});
