import 'package:eduflow_core/eduflow_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final facultyLeavesProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final response = await ref.watch(dioClientProvider).dio.get('/faculty/me/leave-requests');
  final body = Map<String, dynamic>.from(response.data as Map);
  return (body['data'] as List? ?? const []).whereType<Map>().map((item) => Map<String, dynamic>.from(item)).toList();
});

class FacultyLeaveScreen extends ConsumerStatefulWidget {
  const FacultyLeaveScreen({super.key});
  @override
  ConsumerState<FacultyLeaveScreen> createState() => _FacultyLeaveScreenState();
}

class _FacultyLeaveScreenState extends ConsumerState<FacultyLeaveScreen> {
  DateTime? from;
  DateTime? to;
  final reason = TextEditingController();
  final handover = TextEditingController();
  bool saving = false;
  @override
  void dispose() { reason.dispose(); handover.dispose(); super.dispose(); }
  Future<void> pick(bool start) async {
    final value = await showDatePicker(context: context, initialDate: start ? (from ?? DateTime.now()) : (to ?? from ?? DateTime.now()), firstDate: DateTime.now().subtract(const Duration(days: 1)), lastDate: DateTime.now().add(const Duration(days: 730)));
    if (value != null) setState(() { if (start) { from = value; } else { to = value; } });
  }
  Future<void> submit() async {
    if (from == null || to == null || reason.text.trim().isEmpty) return;
    setState(() => saving = true);
    try {
      await ref.read(dioClientProvider).dio.post('/faculty/me/leave-requests', data: {'start_date': from!.toIso8601String().substring(0, 10), 'end_date': to!.toIso8601String().substring(0, 10), 'reason': reason.text.trim(), 'handover_note': handover.text.trim()});
      ref.invalidate(facultyLeavesProvider);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Leave request submitted to Management.')));
    } finally { if (mounted) setState(() => saving = false); }
  }
  String label(DateTime? value) => value == null ? 'Select date' : value.toIso8601String().substring(0, 10);
  @override
  Widget build(BuildContext context) {
    final state = ref.watch(facultyLeavesProvider);
    return Scaffold(appBar: AppBar(title: const Text('Faculty leave'), leading: IconButton(onPressed: () => context.go('/faculty'), icon: const Icon(Icons.arrow_back_rounded))), body: ListView(padding: const EdgeInsets.all(16), children: [
      Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(borderRadius: BorderRadius.circular(26), gradient: const LinearGradient(colors: [Color(0xFF1C255D), Color(0xFF614FEF)])), child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('TEACHING CONTINUITY', style: TextStyle(color: Color(0xFFBFEFFD), fontWeight: FontWeight.w800)), SizedBox(height: 8), Text('Request leave with a clear handover.', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800))])),
      const SizedBox(height: 18),
      Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [Row(children: [Expanded(child: OutlinedButton(onPressed: () => pick(true), child: Text('From: ${label(from)}'))), const SizedBox(width: 10), Expanded(child: OutlinedButton(onPressed: () => pick(false), child: Text('To: ${label(to)}')))]), const SizedBox(height: 12), TextField(controller: reason, maxLines: 3, decoration: const InputDecoration(labelText: 'Reason')), const SizedBox(height: 12), TextField(controller: handover, maxLines: 2, decoration: const InputDecoration(labelText: 'Handover note (optional)')), const SizedBox(height: 16), FilledButton(onPressed: saving ? null : submit, child: const Text('Submit leave request'))]))),
      const SizedBox(height: 22), Text('My requests', style: Theme.of(context).textTheme.titleLarge), const SizedBox(height: 8),
      state.when(loading: () => const Center(child: CircularProgressIndicator()), error: (_, __) => TextButton(onPressed: () => ref.invalidate(facultyLeavesProvider), child: const Text('Retry loading requests')), data: (items) => Column(children: items.map((item) => Card(child: ListTile(title: Text('${item['start_date']} → ${item['end_date']}'), subtitle: Text(item['reason']?.toString() ?? ''), trailing: Text(item['status']?.toString() ?? 'PENDING')))).toList())),
    ]));
  }
}
