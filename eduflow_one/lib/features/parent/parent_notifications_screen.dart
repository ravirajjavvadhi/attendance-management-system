import 'package:eduflow_core/eduflow_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final parentNotificationsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final response = await ref.watch(dioClientProvider).dio.get('/parent/dashboard');
  final body = Map<String, dynamic>.from(response.data as Map);
  final data = Map<String, dynamic>.from(body['data'] as Map? ?? body);
  return (data['notifications'] as List? ?? const []).whereType<Map>().map((item) => Map<String, dynamic>.from(item)).toList();
});

class ParentNotificationsScreen extends ConsumerWidget {
  const ParentNotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(parentNotificationsProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Family inbox'),
        leading: IconButton(onPressed: () => context.go('/parent'), icon: const Icon(Icons.arrow_back_rounded)),
        actions: [IconButton(onPressed: () => ref.invalidate(parentNotificationsProvider), icon: const Icon(Icons.refresh_rounded))],
      ),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => Center(child: FilledButton(onPressed: () => ref.invalidate(parentNotificationsProvider), child: const Text('Try again'))),
        data: (items) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(parentNotificationsProvider),
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            children: [
              const _InboxHero(title: 'FAMILY INBOX', subtitle: 'Attendance, faculty, and campus updates'),
              const SizedBox(height: 18),
              if (items.isEmpty) const Card(child: Padding(padding: EdgeInsets.all(20), child: Text('No notifications right now.'))),
              ...items.map((item) {
                final absent = '${item['title']} ${item['message']}'.toLowerCase().contains('absent');
                return Card(child: ListTile(leading: CircleAvatar(backgroundColor: absent ? Colors.red.withValues(alpha: .15) : null, child: Icon(absent ? Icons.person_off_rounded : Icons.notifications_rounded, color: absent ? Colors.red : null)), title: Text(item['title']?.toString() ?? 'Update'), subtitle: Text('${item['message'] ?? ''}\n${item['date'] ?? ''}', maxLines: 3, overflow: TextOverflow.ellipsis), isThreeLine: true));
              }),
            ],
          ),
        ),
      ),
    );
  }
}

class _InboxHero extends StatelessWidget {
  const _InboxHero({required this.title, required this.subtitle});
  final String title;
  final String subtitle;
  @override
  Widget build(BuildContext context) => Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(borderRadius: BorderRadius.circular(26), gradient: const LinearGradient(colors: [Color(0xFF1C255D), Color(0xFF614FEF)])), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(color: Color(0xFFBFEFFD), fontWeight: FontWeight.w800)), const SizedBox(height: 8), Text(subtitle, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800))]));
}
