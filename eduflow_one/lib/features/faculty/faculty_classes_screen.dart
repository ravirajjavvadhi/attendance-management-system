import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../auth/session.dart';
import '../dashboard/dashboard_repository.dart';

class FacultyClassesScreen extends ConsumerWidget {
  const FacultyClassesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(dashboardProvider(EduFlowRole.faculty));
    return Scaffold(
      appBar: AppBar(title: const Text('My classes'), leading: IconButton(onPressed: () => context.canPop() ? context.pop() : context.go('/faculty'), icon: const Icon(Icons.arrow_back_rounded))),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => Center(child: FilledButton(onPressed: () => ref.invalidate(dashboardProvider(EduFlowRole.faculty)), child: const Text('Retry'))),
        data: (data) {
          final schedule = (data['schedule'] as List? ?? const []).whereType<Map>().map((item) => Map<String, dynamic>.from(item)).toList();
          return ListView(padding: const EdgeInsets.all(16), children: [
            const Text('Teaching schedule', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
            const SizedBox(height: 6),
            const Text('Open a scheduled class to review the roster and submit attendance.'),
            const SizedBox(height: 18),
            if (schedule.isEmpty) const Card(child: Padding(padding: EdgeInsets.all(20), child: Text('No classes are assigned for the current schedule.'))),
            ...schedule.map((slot) => Card(child: ListTile(
              onTap: () => context.push('/faculty/attendance', extra: slot),
              leading: const CircleAvatar(child: Icon(Icons.class_rounded)),
              title: Text(slot['subject_name']?.toString() ?? 'Scheduled class'),
              subtitle: Text('${slot['day'] ?? 'Today'} · Period ${slot['period_number'] ?? '—'} · ${slot['section_name'] ?? 'Section'}'),
              trailing: const Icon(Icons.arrow_forward_rounded),
            ))),
          ]);
        },
      ),
    );
  }
}
