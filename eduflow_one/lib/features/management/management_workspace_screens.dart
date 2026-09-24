import 'package:eduflow_core/eduflow_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final managementWorkspaceRepositoryProvider = Provider<ManagementWorkspaceRepository>(
  (ref) => ManagementWorkspaceRepository(ref.watch(dioClientProvider)),
);

class ManagementWorkspaceRepository {
  ManagementWorkspaceRepository(this._client);
  final DioClient _client;

  Future<Map<String, dynamic>> operations() async {
    final results = await Future.wait([
      _client.dio.get('/attendance/stats/overview'),
      _client.dio.get('/legacy-sms/stats'),
    ]);
    return {
      'attendance': Map<String, dynamic>.from(results[0].data as Map),
      'sms': Map<String, dynamic>.from(results[1].data as Map),
    };
  }

  Future<Map<String, List<Map<String, dynamic>>>> people() async {
    final results = await Future.wait([
      _client.dio.get('/academic/students', queryParameters: {'limit': 60}),
      _client.dio.get('/users/faculty'),
      _client.dio.get('/academic/sections'),
    ]);
    return {
      'students': _rows(results[0].data),
      'faculty': _rows(results[1].data),
      'sections': _rows(results[2].data),
    };
  }

  Future<Map<String, dynamic>> insights() async {
    final response = await _client.dio.get('/management/analytics/enterprise');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<List<Map<String, dynamic>>> smsLogs() async {
    final response = await _client.dio.get('/legacy-notifications/logs', queryParameters: {'limit': 50});
    return _rows(response.data);
  }
}

final managementOperationsProvider = FutureProvider<Map<String, dynamic>>(
  (ref) => ref.watch(managementWorkspaceRepositoryProvider).operations(),
);
final managementPeopleProvider = FutureProvider<Map<String, List<Map<String, dynamic>>>>(
  (ref) => ref.watch(managementWorkspaceRepositoryProvider).people(),
);
final managementInsightsProvider = FutureProvider<Map<String, dynamic>>(
  (ref) => ref.watch(managementWorkspaceRepositoryProvider).insights(),
);
final managementSmsLogsProvider = FutureProvider<List<Map<String, dynamic>>>(
  (ref) => ref.watch(managementWorkspaceRepositoryProvider).smsLogs(),
);

class ManagementOperationsScreen extends ConsumerWidget {
  const ManagementOperationsScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(managementOperationsProvider);
    return _ManagementPage(
      title: 'Operations',
      onRefresh: () async => ref.invalidate(managementOperationsProvider),
      child: state.when(
        loading: () => const _LoadingPanel(),
        error: (error, _) => _FailurePanel(error: error, onRetry: () => ref.invalidate(managementOperationsProvider)),
        data: (data) {
          final attendance = _map(data['attendance']);
          final sms = _map(data['sms']);
          final alerts = _rows(attendance['alerts']);
          final departments = _rows(attendance['department_overview']);
          return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const _WorkspaceHero(eyebrow: 'CAMPUS COMMAND', title: 'Operational pulse', body: 'Live attendance health and message delivery for your institution.'),
            const SizedBox(height: 20),
            _MetricWrap(metrics: [
              _MetricData('Present', '${attendance['present_today'] ?? 0}', Icons.how_to_reg_rounded),
              _MetricData('Absent', '${attendance['absent_today'] ?? 0}', Icons.person_off_rounded),
              _MetricData('SMS queued', '${sms['queue_size'] ?? 0}', Icons.sms_outlined),
              _MetricData('SMS failed', '${sms['failed_today'] ?? 0}', Icons.sms_failed_outlined),
            ]),
            const SizedBox(height: 24),
            _Heading(title: 'Attendance intervention list', caption: 'Learners below the current attendance threshold'),
            const SizedBox(height: 8),
            if (alerts.isEmpty) const _EmptyCard('No attendance interventions are currently reported.') else ...alerts.take(8).map((item) => Card(child: ListTile(leading: const CircleAvatar(child: Icon(Icons.warning_amber_rounded)), title: Text(item['name']?.toString() ?? 'Student'), subtitle: Text(item['class']?.toString() ?? 'Section'), trailing: Text(item['rate']?.toString() ?? '—', style: const TextStyle(fontWeight: FontWeight.w800))))),
            const SizedBox(height: 24),
            _Heading(title: 'Department coverage', caption: 'Present learners as reported today'),
            const SizedBox(height: 8),
            if (departments.isEmpty) const _EmptyCard('Department coverage will appear as attendance is recorded.') else ...departments.take(8).map((item) => _DepartmentTile(item: item)),
          ]);
        },
      ),
    );
  }
}

class ManagementPeopleScreen extends ConsumerStatefulWidget {
  const ManagementPeopleScreen({super.key});

  @override
  ConsumerState<ManagementPeopleScreen> createState() =>
      _ManagementPeopleScreenState();
}

class _ManagementPeopleScreenState extends ConsumerState<ManagementPeopleScreen> {
  String _query = '';

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(managementPeopleProvider);
    return _ManagementPage(
      title: 'People',
      onRefresh: () async => ref.invalidate(managementPeopleProvider),
      child: state.when(
        loading: () => const _LoadingPanel(),
        error: (error, _) => _FailurePanel(error: error, onRetry: () => ref.invalidate(managementPeopleProvider)),
        data: (data) {
          final students = data['students'] ?? const <Map<String, dynamic>>[];
          final faculty = data['faculty'] ?? const <Map<String, dynamic>>[];
          final sections = data['sections'] ?? const <Map<String, dynamic>>[];
          final query = _query.trim().toLowerCase();
          final matchedStudents = query.isEmpty
              ? students
              : students.where((person) {
                  return '${person['name'] ?? ''} ${person['roll_number'] ?? ''} ${person['section_name'] ?? ''}'
                      .toLowerCase()
                      .contains(query);
                }).toList();
          final matchedFaculty = query.isEmpty
              ? faculty
              : faculty.where((person) {
                  return '${person['name'] ?? ''} ${person['email'] ?? ''}'
                      .toLowerCase()
                      .contains(query);
                }).toList();
          return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const _WorkspaceHero(eyebrow: 'CAMPUS PEOPLE', title: 'People & groups', body: 'A mobile-first directory of learners, staff, and academic sections.'),
            const SizedBox(height: 20),
            _MetricWrap(metrics: [
              _MetricData('Students', '${students.length}', Icons.groups_rounded),
              _MetricData('Faculty', '${faculty.length}', Icons.school_rounded),
              _MetricData('Sections', '${sections.length}', Icons.account_tree_outlined),
            ]),
            const SizedBox(height: 24),
            TextField(
              onChanged: (value) => setState(() => _query = value),
              textInputAction: TextInputAction.search,
              decoration: InputDecoration(
                hintText: 'Search learner, roll number, faculty, or section',
                prefixIcon: const Icon(Icons.search_rounded),
                suffixIcon: _query.isEmpty
                    ? null
                    : IconButton(
                        tooltip: 'Clear search',
                        onPressed: () => setState(() => _query = ''),
                        icon: const Icon(Icons.close_rounded),
                      ),
              ),
            ),
            const SizedBox(height: 24),
            _Heading(title: 'Faculty', caption: 'Active staff available in this institution'),
            const SizedBox(height: 8),
            if (matchedFaculty.isEmpty) const _EmptyCard('No faculty records match this search.') else ...matchedFaculty.take(8).map((person) => Card(child: ListTile(leading: CircleAvatar(child: Text(_initial(person['name']))), title: Text(person['name']?.toString() ?? person['email']?.toString() ?? 'Faculty'), subtitle: Text(person['email']?.toString() ?? 'No email recorded')))),
            const SizedBox(height: 24),
            _Heading(title: 'Learners', caption: 'Recent directory entries; full search is the next expansion'),
            const SizedBox(height: 8),
            if (matchedStudents.isEmpty) const _EmptyCard('No learners match this search.') else ...matchedStudents.take(20).map((person) => Card(child: ListTile(leading: CircleAvatar(child: Text(_initial(person['name']))), title: Text(person['name']?.toString() == 'Not Provided' ? 'Student' : person['name']?.toString() ?? 'Student'), subtitle: Text('${person['roll_number'] ?? '—'} · ${person['section_name'] ?? 'Section'}')))),
          ]);
        },
      ),
    );
  }
}

class ManagementInsightsScreen extends ConsumerWidget {
  const ManagementInsightsScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(managementInsightsProvider);
    return _ManagementPage(
      title: 'Insights',
      onRefresh: () async => ref.invalidate(managementInsightsProvider),
      child: state.when(
        loading: () => const _LoadingPanel(),
        error: (error, _) => _FailurePanel(error: error, onRetry: () => ref.invalidate(managementInsightsProvider)),
        data: (data) {
          final findings = _rows(data['ai_insights']);
          final risks = _rows(data['detention_risk_students']);
          final subjects = _rows(data['subject_difficulty']);
          return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const _WorkspaceHero(eyebrow: 'EVIDENCE LEDGER', title: 'Academic insights', body: 'Institution trends with their source metrics, ready for review.'),
            const SizedBox(height: 22),
            _Heading(title: 'Executive findings', caption: 'Generated from attendance and academic summaries'),
            const SizedBox(height: 8),
            if (findings.isEmpty) const _EmptyCard('No executive findings are available yet.') else ...findings.map((item) => Card(child: ListTile(leading: const CircleAvatar(child: Icon(Icons.auto_graph_rounded)), title: Text(item['title']?.toString() ?? 'Finding'), subtitle: Text(item['message']?.toString() ?? ''), trailing: Text(item['severity']?.toString() ?? 'INFO')))),
            const SizedBox(height: 24),
            _Heading(title: 'Attendance risk', caption: 'Learners whose attendance needs a human follow-up'),
            const SizedBox(height: 8),
            if (risks.isEmpty) const _EmptyCard('No attendance-risk records are available.') else ...risks.take(10).map((item) => Card(child: ListTile(leading: const CircleAvatar(child: Icon(Icons.person_search_rounded)), title: Text(item['name']?.toString() ?? 'Student'), subtitle: Text(item['roll_number']?.toString() ?? ''), trailing: Text('${item['attendance_pct'] ?? '—'}%')))),
            const SizedBox(height: 24),
            _Heading(title: 'Subject signals', caption: 'Courses ranked by attendance pressure'),
            const SizedBox(height: 8),
            if (subjects.isEmpty) const _EmptyCard('Subject attendance signals will appear when data is available.') else ...subjects.take(8).map((item) => Card(child: ListTile(title: Text(item['name']?.toString() ?? 'Subject'), subtitle: Text(item['code']?.toString() ?? ''), trailing: Text('${item['average_attendance'] ?? '—'}%')))),
          ]);
        },
      ),
    );
  }
}

class ManagementMoreScreen extends StatelessWidget {
  const ManagementMoreScreen({super.key});
  @override
  Widget build(BuildContext context) => _ManagementPage(
        title: 'Management tools',
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const _WorkspaceHero(eyebrow: 'CONTROL ROOM', title: 'Institution tools', body: 'Open a focused management workflow from one mobile command surface.'),
          const SizedBox(height: 20),
          Card(child: ListTile(onTap: () => context.push('/management/leaves'), leading: const CircleAvatar(child: Icon(Icons.fact_check_rounded)), title: const Text('Leave approvals'), subtitle: const Text('Review and decide pending requests'), trailing: const Icon(Icons.chevron_right_rounded))),
          Card(child: ListTile(onTap: () => context.push('/management/timetable'), leading: const CircleAvatar(child: Icon(Icons.calendar_month_rounded)), title: const Text('Timetable'), subtitle: const Text('Review every section timetable from the mobile Control Room'), trailing: const Icon(Icons.chevron_right_rounded))),
          Card(child: ListTile(onTap: () => context.push('/management/sms-log'), leading: const CircleAvatar(child: Icon(Icons.sms_rounded)), title: const Text('SMS audit log'), subtitle: const Text('Review delivery, failures, recipients, and gateway responses'), trailing: const Icon(Icons.chevron_right_rounded))),
          const Card(child: ListTile(leading: CircleAvatar(child: Icon(Icons.file_present_rounded)), title: Text('Reports'), subtitle: Text('Enterprise analytics is available in the Insights workspace.'))),
        ]),
      );
}

class ManagementSmsLogScreen extends ConsumerWidget {
  const ManagementSmsLogScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(managementSmsLogsProvider);
    return _ManagementPage(
      title: 'SMS audit log',
      onRefresh: () async => ref.invalidate(managementSmsLogsProvider),
      child: state.when(
        loading: () => const _LoadingPanel(),
        error: (error, _) => _FailurePanel(error: error, onRetry: () => ref.invalidate(managementSmsLogsProvider)),
        data: (logs) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const _WorkspaceHero(eyebrow: 'DELIVERY EVIDENCE', title: 'Message audit', body: 'Immutable delivery events from the institution SMS gateway.'),
          const SizedBox(height: 20),
          if (logs.isEmpty)
            const _EmptyCard('No notification delivery events are available.')
          else
            ...logs.map((log) => Card(child: ListTile(
              leading: CircleAvatar(child: Icon(_smsIcon(log['status']?.toString()))),
              title: Text(log['recipient']?.toString() ?? 'Recipient'),
              subtitle: Text(log['message']?.toString() ?? '' , maxLines: 2, overflow: TextOverflow.ellipsis),
              trailing: Text(log['status']?.toString() ?? 'UNKNOWN', style: const TextStyle(fontWeight: FontWeight.w800)),
            ))),
        ]),
      ),
    );
  }
}

class _ManagementPage extends StatelessWidget {
  const _ManagementPage({required this.title, required this.child, this.onRefresh});
  final String title;
  final Widget child;
  final Future<void> Function()? onRefresh;
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: Text(title), leading: IconButton(onPressed: () => context.go('/management'), icon: const Icon(Icons.arrow_back_rounded))), body: RefreshIndicator(onRefresh: onRefresh ?? () async {}, child: ListView(physics: const AlwaysScrollableScrollPhysics(), padding: const EdgeInsets.fromLTRB(16, 12, 16, 32), children: [child])));
}

class _WorkspaceHero extends StatelessWidget { const _WorkspaceHero({required this.eyebrow, required this.title, required this.body}); final String eyebrow; final String title; final String body; @override Widget build(BuildContext context) => Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(borderRadius: BorderRadius.circular(26), gradient: const LinearGradient(colors: [Color(0xFF1C255D), Color(0xFF614FEF)])), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(eyebrow, style: const TextStyle(color: Color(0xFFBFEFFD), fontWeight: FontWeight.w800, letterSpacing: 1.1)), const SizedBox(height: 8), Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(color: Colors.white, fontWeight: FontWeight.w800)), const SizedBox(height: 6), Text(body, style: const TextStyle(color: Color(0xFFE5E9FF), height: 1.35))])); }
class _MetricData { const _MetricData(this.label, this.value, this.icon); final String label; final String value; final IconData icon; }
class _MetricWrap extends StatelessWidget { const _MetricWrap({required this.metrics}); final List<_MetricData> metrics; @override Widget build(BuildContext context) => Wrap(spacing: 8, runSpacing: 8, children: metrics.map((metric) => SizedBox(width: 155, child: Card(child: Padding(padding: const EdgeInsets.all(14), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Icon(metric.icon, color: Theme.of(context).colorScheme.primary), const SizedBox(height: 10), Text(metric.value, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)), Text(metric.label, style: Theme.of(context).textTheme.bodySmall)])))).toList()); }
class _Heading extends StatelessWidget { const _Heading({required this.title, required this.caption}); final String title; final String caption; @override Widget build(BuildContext context) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)), const SizedBox(height: 3), Text(caption, style: Theme.of(context).textTheme.bodySmall)]); }
class _DepartmentTile extends StatelessWidget { const _DepartmentTile({required this.item}); final Map<String, dynamic> item; @override Widget build(BuildContext context) { final rate = _number(item['rate']); return Card(child: Padding(padding: const EdgeInsets.all(14), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Row(children: [Expanded(child: Text(item['department']?.toString() ?? 'Department', style: const TextStyle(fontWeight: FontWeight.w700))), Text('${rate.toStringAsFixed(1)}%')]), const SizedBox(height: 10), LinearProgressIndicator(value: (rate / 100).clamp(0, 1).toDouble())]))); } }
class _EmptyCard extends StatelessWidget { const _EmptyCard(this.message); final String message; @override Widget build(BuildContext context) => Card(child: Padding(padding: const EdgeInsets.all(18), child: Text(message))); }
class _LoadingPanel extends StatelessWidget {
  const _LoadingPanel();

  @override
  Widget build(BuildContext context) => TweenAnimationBuilder<double>(
        duration: const Duration(milliseconds: 900),
        tween: Tween(begin: .35, end: .85),
        curve: Curves.easeInOut,
        builder: (_, opacity, child) => Opacity(opacity: opacity, child: child),
        child: Column(children: const [
          _LoadingBlock(height: 170),
          SizedBox(height: 18),
          _LoadingBlock(height: 92),
          SizedBox(height: 12),
          _LoadingBlock(height: 92),
          SizedBox(height: 12),
          _LoadingBlock(height: 92),
        ]),
      );
}

class _LoadingBlock extends StatelessWidget {
  const _LoadingBlock({required this.height});
  final double height;
  @override
  Widget build(BuildContext context) => Container(
        height: height,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(22),
        ),
      );
}
class _FailurePanel extends StatelessWidget { const _FailurePanel({required this.error, required this.onRetry}); final Object error; final VoidCallback onRetry; @override Widget build(BuildContext context) => Padding(padding: const EdgeInsets.all(28), child: Column(children: [const Icon(Icons.cloud_off_rounded, size: 48), const SizedBox(height: 12), const Text('This workspace could not be loaded.'), const SizedBox(height: 12), FilledButton(onPressed: onRetry, child: const Text('Try again'))])); }
Map<String, dynamic> _map(dynamic value) => value is Map ? Map<String, dynamic>.from(value) : <String, dynamic>{};
List<Map<String, dynamic>> _rows(dynamic value) => value is List ? value.whereType<Map>().map((row) => Map<String, dynamic>.from(row)).toList() : <Map<String, dynamic>>[];
double _number(dynamic value) => value is num ? value.toDouble() : double.tryParse(value?.toString() ?? '') ?? 0;
String _initial(dynamic value) { final text = value?.toString().trim() ?? ''; return text.isEmpty ? '•' : text[0].toUpperCase(); }
IconData _smsIcon(String? status) {
  if (status == 'SENT' || status == 'DELIVERED') {
    return Icons.check_circle_outline_rounded;
  }
  if (status == 'FAILED') return Icons.error_outline_rounded;
  return Icons.schedule_rounded;
}
