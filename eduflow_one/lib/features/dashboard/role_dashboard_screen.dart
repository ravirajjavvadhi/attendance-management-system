import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../auth/session.dart';
import 'dashboard_repository.dart';

class RoleDashboardScreen extends ConsumerWidget {
  const RoleDashboardScreen({super.key, required this.role});
  final EduFlowRole role;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(sessionProvider);
    if (session == null || session.role != role) {
      WidgetsBinding.instance.addPostFrameCallback((_) => context.go('/login'));
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final state = ref.watch(dashboardProvider(role));
    return Scaffold(
      appBar: AppBar(
        title: Text(_titleFor(role)),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: () => ref.invalidate(dashboardProvider(role)),
            icon: const Icon(Icons.refresh_rounded),
          ),
          if (role == EduFlowRole.management)
            IconButton(
              tooltip: 'Management tools',
              onPressed: () => context.push('/management/more'),
              icon: const Icon(Icons.tune_rounded),
            ),
          if (role == EduFlowRole.parent)
            IconButton(
              tooltip: 'Notifications',
              onPressed: () => context.push('/parent/notifications'),
              icon: const Icon(Icons.notifications_none_rounded),
            ),
          if (role == EduFlowRole.student)
            IconButton(
              tooltip: 'Notifications',
              onPressed: () => context.push('/student/notifications'),
              icon: const Icon(Icons.notifications_none_rounded),
            ),
          IconButton(
            tooltip: 'Sign out',
            onPressed: () async {
              await clearSession(ref);
              if (context.mounted) context.go('/login');
            },
            icon: const Icon(Icons.logout_rounded),
          ),
        ],
      ),
      body: state.when(
        loading: () => const _DashboardLoading(),
        error: (error, _) => _DashboardError(
          error: error,
          onRetry: () => ref.invalidate(dashboardProvider(role)),
        ),
        data: (data) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(dashboardProvider(role)),
          child: _DashboardBody(role: role, data: data),
        ),
      ),
      bottomNavigationBar: _RoleNavigation(role: role),
    );
  }
}

class _DashboardBody extends StatelessWidget {
  const _DashboardBody({required this.role, required this.data});
  final EduFlowRole role;
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final content = switch (role) {
      EduFlowRole.student => _StudentDashboard(data: data),
      EduFlowRole.parent => _ParentDashboard(data: data),
      EduFlowRole.faculty => _FacultyDashboard(data: data),
      EduFlowRole.management => _ManagementDashboard(data: data),
      EduFlowRole.unknown => const SizedBox.shrink(),
    };
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
      children: [content],
    );
  }
}

class _StudentDashboard extends StatelessWidget {
  const _StudentDashboard({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final student = _map(data['studentStatus']);
    final stats = _map(data['quickStats']);
    final summary = _map(student['today_summary'] ?? data['todaySummary']);
    final subjects = _list(data['subjectWiseAttendance']);
    final timeline = _list(data['timeline']);
    final timetable = _list(data['todayTimetable']);
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _HeroPanel(
        eyebrow: 'MY MOMENTUM',
        title: 'Good day, ${student['name'] ?? 'Student'}',
        body: summary['status_label']?.toString() ??
            'Your live academic view is ready.',
        badge: 'Roll ${student['roll_number'] ?? '—'}',
      ),
      const SizedBox(height: 18),
      Card(child: ListTile(leading: CircleAvatar(child: Icon(student['current_status']?.toString() == 'LIVE NOW' ? Icons.play_circle_fill_rounded : Icons.schedule_rounded)), title: Text(student['current_subject']?.toString() ?? 'No live class'), subtitle: Text('${student['current_faculty'] ?? 'Faculty'} · ${student['current_room'] ?? 'Room TBA'}'), trailing: Text(student['current_status']?.toString() ?? ''))),
      const SizedBox(height: 18),
      _SectionTitle(
          title: 'Your pulse',
          caption: 'Live attendance and academic progress'),
      const SizedBox(height: 10),
      _MetricGrid(metrics: [
        _Metric('Attendance', _percentage(stats['attendance_percentage']),
            Icons.timeline_rounded),
        _Metric(
            'CGPA', _value(stats['cgpa']), Icons.workspace_premium_outlined),
        _Metric(
            'Credits', _value(stats['credits_earned']), Icons.bolt_outlined),
      ]),
      const SizedBox(height: 24),
      _SectionTitle(
          title: 'Subject momentum',
          caption: 'Each number comes from your own attendance records'),
      const SizedBox(height: 10),
      if (subjects.isEmpty)
        const _EmptyPanel(
            message:
                'Subject attendance will appear after classes are recorded.')
      else
        ...subjects.take(6).map((item) => _ProgressRow(
              title: item['subject']?.toString() ?? 'Subject',
              detail:
                  '${item['total_present'] ?? 0}/${item['total_classes'] ?? 0} classes attended',
              value: _double(item['percentage']) / 100,
            )),
      const SizedBox(height: 24),
      _SectionTitle(
          title: 'Today', caption: 'Timetable and attendance activity'),
      const SizedBox(height: 10),
      if (timeline.isEmpty)
        const _EmptyPanel(
            message: 'No live timetable activity is available today.')
      else
        ...timeline.take(4).map((item) => _TimelineTile(item: item)),
      const SizedBox(height: 24),
      _SectionTitle(title: 'Today’s timetable', caption: 'Live schedule for your section'),
      const SizedBox(height: 10),
      ...timetable.take(6).map((item) => Card(child: ListTile(leading: const CircleAvatar(child: Icon(Icons.menu_book_rounded)), title: Text(item['subject']?.toString() ?? 'Class'), subtitle: Text('${item['time'] ?? 'Time'} · ${item['faculty'] ?? 'Faculty'}'), trailing: Text(item['status']?.toString() ?? '')))),
    ]);
  }
}

class _ParentDashboard extends ConsumerStatefulWidget {
  const _ParentDashboard({required this.data});
  final Map<String, dynamic> data;

  @override
  ConsumerState<_ParentDashboard> createState() => _ParentDashboardState();
}

class _ParentDashboardState extends ConsumerState<_ParentDashboard> {
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _refreshTimer = Timer.periodic(const Duration(minutes: 2), (_) {
      ref.invalidate(dashboardProvider(EduFlowRole.parent));
    });
  }

  @override
  void dispose() { _refreshTimer?.cancel(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final student = _map(widget.data['studentStatus']);
    final stats = _map(widget.data['quickStats']);
    final notifications = _list(widget.data['notifications']);
    final subjects = _list(widget.data['subjectWiseAttendance']);
    final timetable = _list(widget.data['todayTimetable']);
    final live = student['current_status']?.toString() == 'LIVE NOW';
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _HeroPanel(
        eyebrow: 'FAMILY PULSE',
        title: student['name']?.toString() ?? 'Your child',
        body:
            'A clear view of progress, attendance, and the actions that need you.',
        badge: 'Roll ${student['roll_number'] ?? '—'}',
      ),
      const SizedBox(height: 18),
      Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(live ? 'LIVE CLASS NOW' : 'CURRENT CAMPUS STATUS', style: TextStyle(color: live ? Colors.green : Theme.of(context).colorScheme.primary, fontWeight: FontWeight.w800, letterSpacing: 1)), const SizedBox(height: 8), Text(student['current_subject']?.toString() ?? 'No active class', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)), const SizedBox(height: 4), Text('${student['current_faculty'] ?? 'Faculty'} · ${student['current_room'] ?? 'Room TBA'}'), const SizedBox(height: 8), Text('Auto-refreshes every 2 minutes from the published timetable.', style: Theme.of(context).textTheme.bodySmall)]))),
      const SizedBox(height: 18),
      _MetricGrid(metrics: [
        _Metric('Attendance', _percentage(stats['attendance_percentage']),
            Icons.timeline_rounded),
        _Metric(
            'CGPA', _value(stats['cgpa']), Icons.workspace_premium_outlined),
        _Metric(
            'Credits', _value(stats['credits_earned']), Icons.bolt_outlined),
      ]),
      const SizedBox(height: 24),
      _SectionTitle(
          title: 'What needs attention',
          caption: 'Updates linked to your child'),
      const SizedBox(height: 10),
      if (notifications.isEmpty)
        const _EmptyPanel(message: 'There are no new parent updates.')
      else
        ...notifications.take(4).map((item) => _TimelineTile(item: item)),
      const SizedBox(height: 24),
      _SectionTitle(title: 'Today’s timetable', caption: 'Department, year, and section schedule'),
      const SizedBox(height: 10),
      ...timetable.take(6).map((item) => Card(child: ListTile(leading: CircleAvatar(child: Icon(item['status']?.toString() == 'LIVE NOW' ? Icons.play_circle_fill_rounded : Icons.schedule_rounded)), title: Text(item['subject']?.toString() ?? 'Class'), subtitle: Text('${item['time'] ?? 'Time'} · ${item['faculty'] ?? 'Faculty'}'), trailing: Text(item['status']?.toString() ?? '')))),
      const SizedBox(height: 24),
      _SectionTitle(
          title: 'Attendance by subject',
          caption: 'Live record from the institution'),
      const SizedBox(height: 10),
      if (subjects.isEmpty)
        const _EmptyPanel(
            message:
                'Subject attendance will appear after classes are recorded.')
      else
        ...subjects.take(6).map((item) => _ProgressRow(
              title: item['subject']?.toString() ?? 'Subject',
              detail:
                  '${item['total_present'] ?? 0}/${item['total_classes'] ?? 0} classes attended',
              value: _double(item['percentage']) / 100,
            )),
      const SizedBox(height: 18),
      FilledButton.icon(
        onPressed: () => context.push('/parent/leave'),
        icon: const Icon(Icons.event_note_rounded),
        label: const Text('Request student leave'),
      ),
    ]);
  }
}

class _FacultyDashboard extends StatelessWidget {
  const _FacultyDashboard({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final schedule = _map(data['schedule']);
    final day = schedule['current_day']?.toString() ?? 'TODAY';
    final weekly = _map(schedule['schedule']);
    final todaysClasses = _list(weekly[day]);
    final sections = _list(data['sections']);
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _HeroPanel(
        eyebrow: 'TEACHING FLIGHT DECK',
        title: '$day at a glance',
        body: 'Your schedule, sections, and the fastest path to attendance.',
        badge: '${todaysClasses.length} live slots',
      ),
      const SizedBox(height: 22),
      _SectionTitle(
          title: 'Today’s classes',
          caption: 'Live schedule from your assigned timetable'),
      const SizedBox(height: 10),
      if (todaysClasses.isEmpty)
        const _EmptyPanel(message: 'No class slots are scheduled for today.')
      else
        ...todaysClasses.map((item) => _FacultyClassTile(item: item)),
      const SizedBox(height: 24),
      _SectionTitle(
          title: 'Assigned sections',
          caption: 'Select a section to continue attendance'),
      const SizedBox(height: 10),
      Wrap(
          spacing: 8,
          runSpacing: 8,
          children: sections
              .take(10)
              .map((section) => Chip(
                    avatar: const Icon(Icons.groups_rounded, size: 18),
                    label: Text(section['name']?.toString() ?? 'Section'),
                  ))
              .toList()),
      const SizedBox(height: 18),
      FilledButton.icon(
        onPressed: () => context.push('/faculty/learners'),
        icon: const Icon(Icons.groups_rounded),
        label: const Text('Open learner workspace'),
      ),
      const SizedBox(height: 10),
      OutlinedButton.icon(
        onPressed: () => context.push('/faculty/leave'),
        icon: const Icon(Icons.event_busy_rounded),
        label: const Text('Request faculty leave'),
      ),
    ]);
  }
}

class _ManagementDashboard extends StatelessWidget {
  const _ManagementDashboard({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final overview = _map(data['overview']);
    final institution = _map(data['institution']);
    final attention = _list(data['attention']);
    final events = _list(data['upcoming_events']);
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _HeroPanel(
        eyebrow: 'CAMPUS COMMAND',
        title: '${institution['name'] ?? 'Campus'} Control Room',
        body:
            'Live institution operations, decision work, and evidence in one place.',
        badge: data['today']?.toString() ?? 'Live',
      ),
      const SizedBox(height: 18),
      _SectionTitle(
          title: 'Live operations', caption: 'Tenant-scoped records for today'),
      const SizedBox(height: 10),
      _MetricGrid(metrics: [
        _Metric('Students', _value(overview['total_students']),
            Icons.groups_rounded),
        _Metric('Present', _value(overview['present_students']),
            Icons.how_to_reg_rounded),
        _Metric('Rate', _percentage(overview['attendance_rate']),
            Icons.auto_graph_rounded),
      ]),
      const SizedBox(height: 24),
      _SectionTitle(
          title: 'Decision queue',
          caption: 'Items requiring management attention'),
      const SizedBox(height: 10),
      if (attention.isEmpty)
        const _EmptyPanel(message: 'No open management actions right now.')
      else
        ...attention.map((item) => _AttentionTile(item: item)),
      const SizedBox(height: 24),
      _SectionTitle(title: 'Upcoming agenda', caption: 'Institution events'),
      const SizedBox(height: 10),
      if (events.isEmpty)
        const _EmptyPanel(
            message: 'No upcoming institution events are available.')
      else
        ...events.map((item) => _TimelineTile(item: item)),
    ]);
  }
}

class _HeroPanel extends StatelessWidget {
  const _HeroPanel(
      {required this.eyebrow,
      required this.title,
      required this.body,
      required this.badge});
  final String eyebrow;
  final String title;
  final String body;
  final String badge;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
              colors: [Color(0xFF1C255D), Color(0xFF614FEF)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight),
          borderRadius: BorderRadius.circular(28),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(eyebrow,
              style: const TextStyle(
                  color: Color(0xFFBFEFFD),
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.2)),
          const SizedBox(height: 8),
          Text(title,
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall
                  ?.copyWith(color: Colors.white, fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          Text(body,
              style: const TextStyle(color: Color(0xFFE5E9FF), height: 1.4)),
          const SizedBox(height: 18),
          Chip(
              label: Text(badge),
              backgroundColor: Colors.white.withValues(alpha: .16),
              labelStyle: const TextStyle(
                  color: Colors.white, fontWeight: FontWeight.w700)),
        ]),
      );
}

class _MetricGrid extends StatelessWidget {
  const _MetricGrid({required this.metrics});
  final List<_Metric> metrics;
  @override
  Widget build(BuildContext context) =>
      LayoutBuilder(builder: (_, constraints) {
        final width =
            (constraints.maxWidth - 16) / (constraints.maxWidth > 600 ? 3 : 2);
        return Wrap(
            spacing: 8,
            runSpacing: 8,
            children: metrics
                .map((metric) => SizedBox(
                    width: width,
                    child: Card(
                        child: Padding(
                            padding: const EdgeInsets.all(14),
                            child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Icon(metric.icon,
                                      color: Theme.of(context)
                                          .colorScheme
                                          .primary),
                                  const SizedBox(height: 12),
                                  Text(metric.value,
                                      style: Theme.of(context)
                                          .textTheme
                                          .titleLarge
                                          ?.copyWith(
                                              fontWeight: FontWeight.w800)),
                                  const SizedBox(height: 3),
                                  Text(metric.label,
                                      style:
                                          Theme.of(context).textTheme.bodySmall)
                                ])))))
                .toList());
      });
}

class _Metric {
  const _Metric(this.label, this.value, this.icon);
  final String label;
  final String value;
  final IconData icon;
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.title, required this.caption});
  final String title;
  final String caption;
  @override
  Widget build(BuildContext context) =>
      Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title,
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 3),
        Text(caption,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant))
      ]);
}

class _ProgressRow extends StatelessWidget {
  const _ProgressRow(
      {required this.title, required this.detail, required this.value});
  final String title;
  final String detail;
  final double value;
  @override
  Widget build(BuildContext context) => Card(
      child: Padding(
          padding: const EdgeInsets.all(14),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              Expanded(
                  child: Text(title,
                      style: const TextStyle(fontWeight: FontWeight.w700))),
              Text('${(value * 100).round()}%')
            ]),
            const SizedBox(height: 6),
            Text(detail, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 10),
            LinearProgressIndicator(
                value: value.clamp(0, 1).toDouble(),
                borderRadius: BorderRadius.circular(99))
          ])));
}

class _TimelineTile extends StatelessWidget {
  const _TimelineTile({required this.item});
  final Map<String, dynamic> item;
  @override
  Widget build(BuildContext context) {
    final title =
        item['title'] ?? item['subject'] ?? item['subject_name'] ?? 'Update';
    final detail = item['description'] ??
        item['message'] ??
        item['time'] ??
        item['date'] ??
        item['status'] ??
        'Live data';
    return Card(
        child: ListTile(
            leading:
                const CircleAvatar(child: Icon(Icons.auto_awesome_rounded)),
            title: Text(title.toString(),
                maxLines: 1, overflow: TextOverflow.ellipsis),
            subtitle: Text(detail.toString(),
                maxLines: 2, overflow: TextOverflow.ellipsis)));
  }
}

class _FacultyClassTile extends StatelessWidget {
  const _FacultyClassTile({required this.item});
  final Map<String, dynamic> item;

  @override
  Widget build(BuildContext context) {
    final subject = item['subject_name']?.toString() ?? 'Class';
    final section = item['section_name']?.toString() ?? 'Section';
    final status = item['status']?.toString() ?? 'Scheduled';
    return Card(
      child: ListTile(
        onTap: () => context.push('/faculty/attendance', extra: item),
        leading: CircleAvatar(
          backgroundColor: item['is_live'] == true
              ? Theme.of(context).colorScheme.primaryContainer
              : null,
          child: Icon(item['is_live'] == true
              ? Icons.play_circle_fill_rounded
              : Icons.class_rounded),
        ),
        title: Text(subject, maxLines: 1, overflow: TextOverflow.ellipsis),
        subtitle: Text('$section · ${item['time'] ?? 'Time TBA'} · $status'),
        trailing: const Icon(Icons.chevron_right_rounded),
      ),
    );
  }
}

class _AttentionTile extends StatelessWidget {
  const _AttentionTile({required this.item});
  final Map<String, dynamic> item;
  @override
  Widget build(BuildContext context) => Card(
      child: ListTile(
          onTap: item['type']?.toString() == 'LEAVES'
              ? () => context.push('/management/leaves')
              : null,
          leading: const CircleAvatar(child: Icon(Icons.priority_high_rounded)),
          title: Text(item['title']?.toString() ?? 'Action required'),
          subtitle: Text('${item['count'] ?? 0} open item(s)'),
          trailing: item['type']?.toString() == 'LEAVES'
              ? const Icon(Icons.chevron_right_rounded)
              : null));
}

class _EmptyPanel extends StatelessWidget {
  const _EmptyPanel({required this.message});
  final String message;
  @override
  Widget build(BuildContext context) => Card(
      child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(children: [
            Icon(Icons.inbox_outlined,
                color: Theme.of(context).colorScheme.primary),
            const SizedBox(width: 12),
            Expanded(child: Text(message))
          ])));
}

class _DashboardLoading extends StatelessWidget {
  const _DashboardLoading();
  @override
  Widget build(BuildContext context) =>
      const Center(child: CircularProgressIndicator());
}

class _DashboardError extends StatelessWidget {
  const _DashboardError({required this.error, required this.onRetry});
  final Object error;
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => Center(
      child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            const Icon(Icons.cloud_off_rounded, size: 52),
            const SizedBox(height: 14),
            const Text('We could not load this workspace.'),
            const SizedBox(height: 8),
            Text(error.toString(),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis),
            const SizedBox(height: 18),
            FilledButton(onPressed: onRetry, child: const Text('Try again'))
          ])));
}

class _RoleNavigation extends StatelessWidget {
  const _RoleNavigation({required this.role});
  final EduFlowRole role;
  @override
  Widget build(BuildContext context) {
    final items = switch (role) {
      EduFlowRole.student => const [
          ('Today', Icons.home_outlined),
          ('Learn', Icons.auto_stories_outlined),
          ('Progress', Icons.insights_outlined),
          ('Inbox', Icons.mail_outline)
        ],
      EduFlowRole.faculty => const [
          ('Today', Icons.home_outlined),
          ('Classes', Icons.class_outlined),
          ('Learners', Icons.groups_outlined),
          ('Insights', Icons.insights_outlined)
        ],
      EduFlowRole.parent => const [
          ('Family', Icons.family_restroom_outlined),
          ('Progress', Icons.insights_outlined),
          ('Actions', Icons.task_alt_outlined),
          ('Inbox', Icons.mail_outline)
        ],
      EduFlowRole.management => const [
          ('Command', Icons.dashboard_customize_outlined),
          ('Operations', Icons.hub_outlined),
          ('People', Icons.groups_outlined),
          ('Insights', Icons.insights_outlined)
        ],
      EduFlowRole.unknown => const [('Home', Icons.home_outlined)]
    };
    return NavigationBar(
        selectedIndex: 0,
        onDestinationSelected: role == EduFlowRole.management
            ? (index) {
                const routes = [
                  '/management',
                  '/management/operations',
                  '/management/people',
                  '/management/insights',
                ];
                context.go(routes[index]);
              }
            : null,
        destinations: items
            .map((item) =>
                NavigationDestination(icon: Icon(item.$2), label: item.$1))
            .toList());
  }
}

Map<String, dynamic> _map(dynamic value) =>
    value is Map ? Map<String, dynamic>.from(value) : <String, dynamic>{};
List<Map<String, dynamic>> _list(dynamic value) => value is List
    ? value
        .whereType<Map>()
        .map((item) => Map<String, dynamic>.from(item))
        .toList()
    : <Map<String, dynamic>>[];
double _double(dynamic value) => value is num
    ? value.toDouble()
    : double.tryParse(value?.toString() ?? '') ?? 0;
String _value(dynamic value) => value == null ? '—' : value.toString();
String _percentage(dynamic value) =>
    '${_double(value).toStringAsFixed(_double(value) % 1 == 0 ? 0 : 1)}%';
String _titleFor(EduFlowRole role) => switch (role) {
      EduFlowRole.student => 'EduFlow · Student',
      EduFlowRole.faculty => 'EduFlow · Faculty',
      EduFlowRole.parent => 'EduFlow · Parent',
      EduFlowRole.management => 'EduFlow · Management',
      EduFlowRole.unknown => 'EduFlow'
    };
