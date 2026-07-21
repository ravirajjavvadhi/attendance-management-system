import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router/app_router.dart';
import 'core/notification/notification_helper.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:shared_preferences/shared_preferences.dart';

final themeModeProvider = StateProvider<ThemeMode>((ref) => ThemeMode.light);

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Core Services
  await HiveService.init();
  await NotificationHelper.init();
  
  final prefs = await SharedPreferences.getInstance();
  final authService = AuthService(prefs);
  
  // Load saved theme preference
  final isDarkMode = prefs.getBool('isDarkMode') ?? false;

  runApp(
    ProviderScope(
      overrides: [
        authServiceProvider.overrideWithValue(authService),
      ],
      child: EduFlowParentApp(initialIsDarkMode: isDarkMode),
    ),
  );
}

class EduFlowParentApp extends ConsumerWidget {
  final bool initialIsDarkMode;
  const EduFlowParentApp({super.key, required this.initialIsDarkMode});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeModeProvider);

    // Initial theme set on first run (optional enhancement)
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (ref.read(themeModeProvider) == ThemeMode.light && initialIsDarkMode) {
        ref.read(themeModeProvider.notifier).state = ThemeMode.dark;
      }
    });

    return MaterialApp.router(
      title: 'EduFlow Parent',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: router,
    );
  }
}
