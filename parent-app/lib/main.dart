import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router/app_router.dart';
import 'core/notification/notification_helper.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Core Services
  await HiveService.init();
  await NotificationHelper.init();
  
  final prefs = await SharedPreferences.getInstance();
  final authService = AuthService(prefs);

  runApp(
    ProviderScope(
      overrides: [
        authServiceProvider.overrideWithValue(authService),
      ],
      child: const EduFlowParentApp(),
    ),
  );
}

class EduFlowParentApp extends ConsumerWidget {
  const EduFlowParentApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: 'EduFlow Parent',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system, // Supports dark/light mode switching
      routerConfig: router,
    );
  }
}
