import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../auth/session.dart';
import '../dashboard/dashboard_repository.dart';

class FacultyInsightsScreen extends ConsumerWidget {
  const FacultyInsightsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(dashboardProvider(EduFlowRole.faculty));
    return Scaffold(
      appBar: AppBar(title: const Text('Teaching insights'), leading: IconButton(onPressed: () => context.canPop() ? context.pop() : context.go('/faculty'), icon: const Icon(Icons.arrow_back_rounded))),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => Center(child: FilledButton(onPressed: () => ref.invalidate(dashboardProvider(EduFlowRole.faculty)), child: const Text('Retry'))),
        data: (data) {
          final schedule = (data['schedule'] as List? ?? const []).whereType<Map>().length;
          final sections = (data['permitted_sections'] as List? ?? const []).whereType<Map>().length;
          return ListView(padding: const EdgeInsets.all(16), children: [
            const Text('Your teaching pulse', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
            const SizedBox(height: 18),
            Row(children: [Expanded(child: _Metric(value: '$schedule', label: 'Scheduled classes')), const SizedBox(width: 12), Expanded(child: _Metric(value: '$sections', label: 'Linked sections'))]),
            const SizedBox(height: 18),
            Card(child: ListTile(leading: const Icon(Icons.groups_rounded), title: const Text('Learner communication'), subtitle: const Text('Search a roll number, send a parent update, or add an academic remark.'), trailing: const Icon(Icons.arrow_forward_rounded), onTap: () => context.push('/faculty/learners'))),
            Card(child: ListTile(leading: const Icon(Icons.event_note_rounded), title: const Text('Leave and handover'), subtitle: const Text('Submit leave requests and track Management approval.'), trailing: const Icon(Icons.arrow_forward_rounded), onTap: () => context.push('/faculty/leave'))),
          ]);
        },
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  const _Metric({required this.value, required this.label});
  final String value;
  final String label;
  @override
  Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(value, style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800)), const SizedBox(height: 6), Text(label)])));
}
