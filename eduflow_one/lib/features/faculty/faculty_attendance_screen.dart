import 'package:eduflow_core/eduflow_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final facultyAttendanceRepositoryProvider = Provider<FacultyAttendanceRepository>(
  (ref) => FacultyAttendanceRepository(ref.watch(dioClientProvider)),
);

class FacultyAttendanceRepository {
  FacultyAttendanceRepository(this._client);
  final DioClient _client;

  Future<List<Map<String, dynamic>>> roster(int sectionId) async {
    final response = await _client.dio.get('/academic/students', queryParameters: {
      'section_id': sectionId,
    });
    final rows = response.data as List? ?? const [];
    return rows.whereType<Map>().map((row) => Map<String, dynamic>.from(row)).toList();
  }

  Future<Map<int, bool>?> savedStatus({
    required int sectionId,
    required String date,
    required int period,
  }) async {
    final response = await _client.dio.get('/attendance/status', queryParameters: {
      'section_id': sectionId,
      'date': date,
      'period': period,
    });
    final body = Map<String, dynamic>.from(response.data as Map);
    if (body['marked'] != true) return null;
    return (body['records'] as List? ?? const []).whereType<Map>().fold(<int, bool>{},
        (records, row) {
      final studentId = _asInt(row['student_id']);
      if (studentId != null) records[studentId] = row['is_present'] == true;
      return records;
    });
  }

  Future<void> submit({
    required int sectionId,
    required String date,
    required int period,
    required Map<int, bool> presence,
  }) async {
    await _client.dio.post('/attendance/submit', data: {
      'section_id': sectionId,
      'date': date,
      'period': period,
      'records': presence.entries
          .map((entry) => {
                'student_id': entry.key,
                'is_present': entry.value,
              })
          .toList(),
    });
  }
}

class FacultyAttendanceScreen extends ConsumerStatefulWidget {
  const FacultyAttendanceScreen({super.key, required this.classSlot});
  final Map<String, dynamic> classSlot;

  @override
  ConsumerState<FacultyAttendanceScreen> createState() => _FacultyAttendanceScreenState();
}

class _FacultyAttendanceScreenState extends ConsumerState<FacultyAttendanceScreen> {
  late final int? _sectionId = _asInt(widget.classSlot['section_id']);
  late final int? _period = _asInt(widget.classSlot['period_number']);
  late final String _date = _dateString(DateTime.now());
  List<Map<String, dynamic>> _students = const [];
  Map<int, bool> _presence = {};
  bool _loading = true;
  bool _submitting = false;
  bool _wasMarked = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    if (_sectionId == null || _period == null) {
      setState(() => _loading = false);
      return;
    }
    setState(() => _loading = true);
    try {
      final repository = ref.read(facultyAttendanceRepositoryProvider);
      final results = await Future.wait([
        repository.roster(_sectionId!),
        repository.savedStatus(
          sectionId: _sectionId!,
          date: _date,
          period: _period!,
        ),
      ]);
      final students = results[0] as List<Map<String, dynamic>>;
      final saved = results[1] as Map<int, bool>?;
      if (!mounted) return;
      setState(() {
        _students = students;
        _wasMarked = saved != null;
        _presence = {
          for (final student in students)
            if (_asInt(student['id']) case final studentId?)
              studentId: saved?[studentId] ?? true,
        };
      });
    } catch (error) {
      if (mounted) _show('Could not load this class: $error');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _submit() async {
    if (_sectionId == null || _period == null || _presence.isEmpty) return;
    setState(() => _submitting = true);
    try {
      await ref.read(facultyAttendanceRepositoryProvider).submit(
            sectionId: _sectionId!,
            date: _date,
            period: _period!,
            presence: _presence,
          );
      if (!mounted) return;
      _show('Attendance saved. Parents and student timelines are now updated.');
      setState(() => _wasMarked = true);
    } catch (error) {
      if (mounted) _show('Could not save attendance: $error');
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  void _show(String message) => ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );

  @override
  Widget build(BuildContext context) {
    final present = _presence.values.where((value) => value).length;
    final subject = widget.classSlot['subject_name']?.toString() ?? 'Class attendance';
    final section = widget.classSlot['section_name']?.toString() ?? 'Assigned section';
    return Scaffold(
      appBar: AppBar(
        title: const Text('Attendance studio'),
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.arrow_back_rounded),
        ),
        actions: [IconButton(onPressed: _loading ? null : _load, icon: const Icon(Icons.refresh_rounded))],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _sectionId == null || _period == null
              ? const Center(child: Text('This class slot is missing its attendance details.'))
              : Column(children: [
                  _ClassBrief(
                    subject: subject,
                    section: section,
                    time: widget.classSlot['time']?.toString() ?? 'Scheduled class',
                    date: _date,
                    present: present,
                    total: _students.length,
                    wasMarked: _wasMarked,
                  ),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 14, 16, 6),
                    child: Row(children: [
                      Text('Learners', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
                      const Spacer(),
                      TextButton.icon(
                        onPressed: _students.isEmpty
                            ? null
                            : () => setState(() {
                                  for (final student in _students) {
                                    final id = _asInt(student['id']);
                                    if (id != null) _presence[id] = true;
                                  }
                                }),
                        icon: const Icon(Icons.done_all_rounded),
                        label: const Text('All present'),
                      ),
                    ]),
                  ),
                  Expanded(
                    child: _students.isEmpty
                        ? const Center(child: Text('No learners are enrolled in this section.'))
                        : ListView.builder(
                            padding: const EdgeInsets.fromLTRB(16, 4, 16, 12),
                            itemCount: _students.length,
                            itemBuilder: (_, index) {
                              final student = _students[index];
                              final id = _asInt(student['id'])!;
                              final isPresent = _presence[id] ?? true;
                              return Card(
                                child: ListTile(
                                  leading: CircleAvatar(child: Text(_initials(student['name']))),
                                  title: Text(student['name']?.toString() == 'Not Provided' ? 'Student' : student['name']?.toString() ?? 'Student'),
                                  subtitle: Text(student['roll_number']?.toString() ?? 'Roll number unavailable'),
                                  trailing: SegmentedButton<bool>(
                                    showSelectedIcon: false,
                                    segments: const [
                                      ButtonSegment(value: true, label: Text('P')),
                                      ButtonSegment(value: false, label: Text('A')),
                                    ],
                                    selected: {isPresent},
                                    onSelectionChanged: (selected) => setState(() => _presence[id] = selected.first),
                                  ),
                                ),
                              );
                            },
                          ),
                  ),
                  SafeArea(
                    top: false,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: SizedBox(
                        width: double.infinity,
                        child: FilledButton.icon(
                          onPressed: _submitting || _presence.isEmpty ? null : _submit,
                          icon: _submitting
                              ? const SizedBox.square(dimension: 18, child: CircularProgressIndicator(strokeWidth: 2))
                              : const Icon(Icons.cloud_done_rounded),
                          label: Text(_wasMarked ? 'Update attendance' : 'Save attendance'),
                        ),
                      ),
                    ),
                  ),
                ]),
    );
  }
}

class _ClassBrief extends StatelessWidget {
  const _ClassBrief({required this.subject, required this.section, required this.time, required this.date, required this.present, required this.total, required this.wasMarked});
  final String subject;
  final String section;
  final String time;
  final String date;
  final int present;
  final int total;
  final bool wasMarked;

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        margin: const EdgeInsets.fromLTRB(16, 8, 16, 0),
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(24),
          gradient: const LinearGradient(colors: [Color(0xFF1C255D), Color(0xFF614FEF)]),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(wasMarked ? 'SAVED · EDITABLE' : 'LIVE CLASS', style: const TextStyle(color: Color(0xFFBFEFFD), fontWeight: FontWeight.w800, letterSpacing: 1.1)),
          const SizedBox(height: 7),
          Text(subject, style: Theme.of(context).textTheme.titleLarge?.copyWith(color: Colors.white, fontWeight: FontWeight.w800)),
          const SizedBox(height: 5),
          Text('$section · $time · $date', style: const TextStyle(color: Color(0xFFE5E9FF))),
          const SizedBox(height: 16),
          Text('$present of $total marked present', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
        ]),
      );
}

int? _asInt(dynamic value) => value is int ? value : int.tryParse(value?.toString() ?? '');
String _dateString(DateTime value) => '${value.year.toString().padLeft(4, '0')}-${value.month.toString().padLeft(2, '0')}-${value.day.toString().padLeft(2, '0')}';
String _initials(dynamic value) {
  final words = value?.toString().trim().split(RegExp(r'\s+')) ?? const <String>[];
  final initials = words
      .where((word) => word.isNotEmpty)
      .take(2)
      .map((word) => word[0])
      .join()
      .toUpperCase();
  return initials.isEmpty ? 'S' : initials;
}
