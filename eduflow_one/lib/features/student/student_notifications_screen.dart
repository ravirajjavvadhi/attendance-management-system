import 'package:eduflow_core/eduflow_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final studentNotificationsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final response = await ref.watch(dioClientProvider).dio.get('/student/me/dashboard');
  final body = Map<String, dynamic>.from(response.data as Map);
  final data = Map<String, dynamic>.from(body['data'] as Map? ?? body);
  return (data['notifications'] as List? ?? const []).whereType<Map>().map((item) => Map<String, dynamic>.from(item)).toList();
});

class StudentNotificationsScreen extends ConsumerWidget {
  const StudentNotificationsScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(studentNotificationsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Student inbox'), leading: IconButton(onPressed: () => context.go('/student'), icon: const Icon(Icons.arrow_back_rounded))),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => Center(child: FilledButton(onPressed: () => ref.invalidate(studentNotificationsProvider), child: const Text('Try again'))),
        data: (items) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(studentNotificationsProvider),
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            children: [
              const _StudentInboxHero(),
              const SizedBox(height: 18),
              if (items.isEmpty) const Card(child: Padding(padding: EdgeInsets.all(20), child: Text('No new student updates.'))),
              ...items.map((item) => Card(child: ListTile(leading: const CircleAvatar(child: Icon(Icons.notifications_rounded)), title: Text(item['title']?.toString() ?? 'Update'), subtitle: Text('${item['message'] ?? ''}\n${item['date'] ?? ''}', maxLines: 3, overflow: TextOverflow.ellipsis), isThreeLine: true))),
            ],
          ),
        ),
      ),
    );
  }
}

class _StudentInboxHero extends StatelessWidget {
  const _StudentInboxHero();
  @override
  Widget build(BuildContext context) => Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(borderRadius: BorderRadius.circular(26), gradient: const LinearGradient(colors: [Color(0xFF1C255D), Color(0xFF614FEF)])), child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('MY INBOX', style: TextStyle(color: Color(0xFFBFEFFD), fontWeight: FontWeight.w800)), SizedBox(height: 8), Text('Academic and campus updates', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800))]));
}
