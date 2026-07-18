import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'core/router/app_router.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Core Services
  final hiveService = HiveService();
  await hiveService.init();
  
  final authService = AuthService();
  await authService.init();

  runApp(
    ProviderScope(
      overrides: [
        hiveServiceProvider.overrideWithValue(hiveService),
        authServiceProvider.overrideWithValue(authService),
      ],
      child: const FacultyApp(),
    ),
  );
}

class FacultyApp extends ConsumerWidget {
  const FacultyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp.router(
      title: 'EduFlow Faculty',
      theme: EduFlowTheme.lightTheme,
      darkTheme: EduFlowTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: router,
    );
  }
}
