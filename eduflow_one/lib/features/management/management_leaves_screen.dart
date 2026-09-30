import 'package:eduflow_core/eduflow_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final managementLeavesRepositoryProvider = Provider<ManagementLeavesRepository>(
  (ref) => ManagementLeavesRepository(ref.watch(dioClientProvider)),
);

final managementLeavesProvider = FutureProvider<List<Map<String, dynamic>>>((ref) {
  return ref.watch(managementLeavesRepositoryProvider).load();
});

class ManagementLeavesRepository {
  ManagementLeavesRepository(this._client);
  final DioClient _client;

  Future<List<Map<String, dynamic>>> load() async {
    final response = await _client.dio.get('/management/leaves');
    final body = Map<String, dynamic>.from(response.data as Map);
    final rows = body['data'] as List? ?? const [];
    return rows.whereType<Map>().map((row) => Map<String, dynamic>.from(row)).toList();
  }

  Future<void> decide(int leaveId, String status) async {
    await _client.dio.put('/management/leaves/$leaveId/status', data: {'status': status});
  }
}

class ManagementLeavesScreen extends ConsumerWidget {
  const ManagementLeavesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final leaves = ref.watch(managementLeavesProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Leave decision queue'),
        leading: IconButton(onPressed: () => context.pop(), icon: const Icon(Icons.arrow_back_rounded)),
        actions: [IconButton(onPressed: () => ref.invalidate(managementLeavesProvider), icon: const Icon(Icons.refresh_rounded))],
      ),
      body: leaves.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _RetryPanel(error: error, onRetry: () => ref.invalidate(managementLeavesProvider)),
        data: (items) {
          final pending = items.where((leave) => leave['status']?.toString().toUpperCase() == 'PENDING').toList();
          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(managementLeavesProvider),
            child: ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
              children: [
                _QueueHero(pendingCount: pending.length),
                const SizedBox(height: 20),
                Text('Awaiting a decision', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 8),
                if (pending.isEmpty)
                  const _EmptyQueue()
                else
                  ...pending.map((leave) => _LeaveCard(leave: leave)),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _LeaveCard extends ConsumerStatefulWidget {
  const _LeaveCard({required this.leave});
  final Map<String, dynamic> leave;

  @override
  ConsumerState<_LeaveCard> createState() => _LeaveCardState();
}

class _LeaveCardState extends ConsumerState<_LeaveCard> {
  String? _saving;

  Future<void> _decide(String status) async {
    final id = _intValue(widget.leave['id']);
    if (id == null) return;
    setState(() => _saving = status);
    try {
      await ref.read(managementLeavesRepositoryProvider).decide(id, status);
      ref.invalidate(managementLeavesProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Leave request $status.')));
    } catch (error) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Could not record this decision: $error')));
    } finally {
      if (mounted) setState(() => _saving = null);
    }
  }

  @override
  Widget build(BuildContext context) => Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              CircleAvatar(child: Text(_initial(widget.leave['student_name']))),
              const SizedBox(width: 10),
              Expanded(child: Text(widget.leave['student_name']?.toString() ?? 'Student', style: const TextStyle(fontWeight: FontWeight.w800))),
              const Icon(Icons.pending_actions_rounded),
            ]),
            const SizedBox(height: 14),
            Text('${widget.leave['start_date'] ?? '—'}  →  ${widget.leave['end_date'] ?? '—'}', style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),
            Text(widget.leave['reason']?.toString() ?? 'No reason was supplied.'),
            const SizedBox(height: 14),
            Row(children: [
              Expanded(child: OutlinedButton(onPressed: _saving == null ? () => _decide('REJECTED') : null, child: _saving == 'REJECTED' ? const SizedBox.square(dimension: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Text('Reject'))),
              const SizedBox(width: 10),
              Expanded(child: FilledButton(onPressed: _saving == null ? () => _decide('APPROVED') : null, child: _saving == 'APPROVED' ? const SizedBox.square(dimension: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Text('Approve'))),
            ]),
          ]),
        ),
      );
}

class _QueueHero extends StatelessWidget {
  const _QueueHero({required this.pendingCount});
  final int pendingCount;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(26), gradient: const LinearGradient(colors: [Color(0xFF1C255D), Color(0xFF614FEF)])),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('CAMPUS COMMAND', style: TextStyle(color: Color(0xFFBFEFFD), fontWeight: FontWeight.w800, letterSpacing: 1.1)),
          const SizedBox(height: 8),
          Text('$pendingCount request${pendingCount == 1 ? '' : 's'} need a decision', style: Theme.of(context).textTheme.titleLarge?.copyWith(color: Colors.white, fontWeight: FontWeight.w800)),
          const SizedBox(height: 6),
          const Text('Each action is recorded against your management account.', style: TextStyle(color: Color(0xFFE5E9FF))),
        ]),
      );
}

class _EmptyQueue extends StatelessWidget {
  const _EmptyQueue();
  @override
  Widget build(BuildContext context) => const Card(child: Padding(padding: EdgeInsets.all(20), child: Text('No leave requests are waiting for a decision.')));
}

class _RetryPanel extends StatelessWidget {
  const _RetryPanel({required this.error, required this.onRetry});
  final Object error;
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => Center(child: Padding(padding: const EdgeInsets.all(28), child: Column(mainAxisSize: MainAxisSize.min, children: [const Icon(Icons.cloud_off_rounded, size: 46), const SizedBox(height: 12), const Text('The decision queue could not be loaded.'), const SizedBox(height: 12), FilledButton(onPressed: onRetry, child: const Text('Try again'))])));
}

int? _intValue(dynamic value) => value is int ? value : int.tryParse(value?.toString() ?? '');
String _initial(dynamic value) {
  final name = value?.toString().trim() ?? '';
  return name.isEmpty ? 'S' : name[0].toUpperCase();
}
