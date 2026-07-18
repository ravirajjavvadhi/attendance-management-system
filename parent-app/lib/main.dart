import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router/app_router.dart';
import 'package:eduflow_core/eduflow_core.dart';

void main() {
  runApp(
    const ProviderScope(
      child: EduFlowParentApp(),
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
