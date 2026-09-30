import 'package:eduflow_core/eduflow_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final managementTimetableRepositoryProvider = Provider<ManagementTimetableRepository>(
  (ref) => ManagementTimetableRepository(ref.watch(dioClientProvider)),
);

class ManagementTimetableRepository {
  ManagementTimetableRepository(this._client);
  final DioClient _client;

  Future<List<Map<String, dynamic>>> sections() async {
    final response = await _client.dio.get('/academic/sections');
    return _rows(response.data);
  }

  Future<Map<String, List<Map<String, dynamic>>>> timetable(int sectionId) async {
    final response = await _client.dio.get('/academic/timetable/$sectionId');
    final raw = Map<String, dynamic>.from(response.data as Map);
    return raw.map((day, slots) => MapEntry(day, _rows(slots)));
  }
}

final managementTimetableSectionsProvider = FutureProvider<List<Map<String, dynamic>>>(
  (ref) => ref.watch(managementTimetableRepositoryProvider).sections(),
);
final managementTimetableProvider = FutureProvider.family<Map<String, List<Map<String, dynamic>>>, int>(
  (ref, sectionId) => ref.watch(managementTimetableRepositoryProvider).timetable(sectionId),
);

class ManagementTimetableScreen extends ConsumerStatefulWidget {
  const ManagementTimetableScreen({super.key});

  @override
  ConsumerState<ManagementTimetableScreen> createState() => _ManagementTimetableScreenState();
}

class _ManagementTimetableScreenState extends ConsumerState<ManagementTimetableScreen> {
  int? _sectionId;

  @override
  Widget build(BuildContext context) {
    final sectionsState = ref.watch(managementTimetableSectionsProvider);
    final scheduleState = _sectionId == null ? null : ref.watch(managementTimetableProvider(_sectionId!));
    return Scaffold(
      appBar: AppBar(
        title: const Text('Timetable studio'),
        leading: IconButton(onPressed: () => context.go('/management/more'), icon: const Icon(Icons.arrow_back_rounded)),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: () {
              ref.invalidate(managementTimetableSectionsProvider);
              if (_sectionId != null) ref.invalidate(managementTimetableProvider(_sectionId!));
            },
            icon: const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: sectionsState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _ErrorState(onRetry: () => ref.invalidate(managementTimetableSectionsProvider)),
        data: (sections) {
          final sectionItems = sections
              .map((section) {
                final id = _asInt(section['id']);
                return id == null
                    ? null
                    : DropdownMenuItem<int>(
                        value: id,
                        child: Text(section['name']?.toString() ?? 'Section'),
                      );
              })
              .whereType<DropdownMenuItem<int>>()
              .toList();
          return ListView(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
            children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(26),
                gradient: const LinearGradient(colors: [Color(0xFF1C255D), Color(0xFF614FEF)]),
              ),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('ACADEMIC FLOW', style: TextStyle(color: Color(0xFFBFEFFD), fontWeight: FontWeight.w800, letterSpacing: 1.1)),
                const SizedBox(height: 8),
                Text('Timetable studio', style: Theme.of(context).textTheme.titleLarge?.copyWith(color: Colors.white, fontWeight: FontWeight.w800)),
                const SizedBox(height: 6),
                const Text('Select a section to inspect its live timetable.', style: TextStyle(color: Color(0xFFE5E9FF))),
              ]),
            ),
            const SizedBox(height: 18),
            DropdownButtonFormField<int>(
              value: _sectionId,
              isExpanded: true,
              decoration: const InputDecoration(labelText: 'Section', prefixIcon: Icon(Icons.groups_rounded)),
              hint: const Text('Choose a section'),
              items: sectionItems,
              onChanged: (value) => setState(() => _sectionId = value),
            ),
            const SizedBox(height: 22),
            if (_sectionId == null)
              const _TimetableEmpty('Choose a section to view the timetable.')
            else
              scheduleState!.when(
                loading: () => const Padding(padding: EdgeInsets.all(36), child: Center(child: CircularProgressIndicator())),
                error: (error, _) => _ErrorState(onRetry: () => ref.invalidate(managementTimetableProvider(_sectionId!))),
                data: (schedule) => _WeekSchedule(schedule: schedule),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _WeekSchedule extends StatelessWidget {
  const _WeekSchedule({required this.schedule});
  final Map<String, List<Map<String, dynamic>>> schedule;
  @override
  Widget build(BuildContext context) {
    const days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];
    final populated = days.where((day) => (schedule[day] ?? const []).isNotEmpty).toList();
    if (populated.isEmpty) return const _TimetableEmpty('No timetable slots are published for this section.');
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: populated.map((day) => Padding(padding: const EdgeInsets.only(bottom: 18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(_titleCase(day), style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)), const SizedBox(height: 8), ...schedule[day]!.map((slot) => Card(child: ListTile(leading: CircleAvatar(child: Icon(slot['is_break'] == true ? Icons.coffee_rounded : Icons.menu_book_rounded)), title: Text(slot['is_break'] == true ? 'Break' : slot['subject_name']?.toString() ?? 'Subject'), subtitle: Text('${slot['start_time'] ?? ''} – ${slot['end_time'] ?? ''}\n${slot['faculty_name'] ?? 'Faculty TBA'}'), isThreeLine: true, trailing: Text('P${slot['period_number'] ?? '—'}', style: const TextStyle(fontWeight: FontWeight.w800)))))]))).toList());
  }
}

class _TimetableEmpty extends StatelessWidget { const _TimetableEmpty(this.message); final String message; @override Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.all(20), child: Text(message))); }
class _ErrorState extends StatelessWidget { const _ErrorState({required this.onRetry}); final VoidCallback onRetry; @override Widget build(BuildContext context) => Padding(padding: const EdgeInsets.all(28), child: Column(children: [const Icon(Icons.cloud_off_rounded, size: 48), const SizedBox(height: 12), const Text('This timetable could not be loaded.'), const SizedBox(height: 12), FilledButton(onPressed: onRetry, child: const Text('Try again'))])); }
List<Map<String, dynamic>> _rows(dynamic value) => value is List ? value.whereType<Map>().map((item) => Map<String, dynamic>.from(item)).toList() : <Map<String, dynamic>>[];
int? _asInt(dynamic value) => value is int ? value : int.tryParse(value?.toString() ?? '');
String _titleCase(String value) => value.substring(0, 1) + value.substring(1).toLowerCase();
