import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:go_router/go_router.dart';
import 'dart:async';
import '../../../../core/notification/notification_helper.dart';

// Provide the dashboard data
final parentDashboardProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final dioClient = ref.watch(dioClientProvider);
  final response = await dioClient.dio.get('/parent/dashboard');
  return response.data['data'];
});

class HomeDashboardScreen extends ConsumerStatefulWidget {
  const HomeDashboardScreen({super.key});

  @override
  ConsumerState<HomeDashboardScreen> createState() => _HomeDashboardScreenState();
}

class _HomeDashboardScreenState extends ConsumerState<HomeDashboardScreen> {
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    // Auto-refresh every 60 seconds for live timetable accuracy
    _refreshTimer = Timer.periodic(const Duration(seconds: 60), (_) {
      ref.invalidate(parentDashboardProvider);
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Map<String, dynamic>? _getCurrentLiveClass(List<dynamic> todayTimetable) {
    if (todayTimetable.isEmpty || todayTimetable[0]['subject'] == 'No classes scheduled today') {
      return null;
    }

    final now = DateTime.now();
    for (var tt in todayTimetable) {
      try {
        final timeStr = tt['time'] as String;
        final parts = timeStr.split('-');
        if (parts.length == 2) {
          final startParts = parts[0].trim().split(':');
          final endParts = parts[1].trim().split(':');

          final start = DateTime(now.year, now.month, now.day, int.parse(startParts[0]), int.parse(startParts[1]));
          final end = DateTime(now.year, now.month, now.day, int.parse(endParts[0]), int.parse(endParts[1]));

          if (now.isAfter(start) && now.isBefore(end)) {
            if (tt['subject'].toString().toLowerCase().contains('break')) {
              continue;
            }
            return tt;
          }
        }
      } catch (e) {
        // Parse error, skip
      }
    }
    return null;
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  }

  String _getRelativeDate(String dateStr) {
    try {
      final eventDate = DateTime.parse(dateStr);
      final now = DateTime.now();
      final diff = eventDate.difference(now).inDays;
      if (diff == 0) return 'Today';
      if (diff == 1) return 'Tomorrow';
      if (diff < 0) return '${-diff} days ago';
      return 'In $diff days';
    } catch (_) {
      return dateStr;
    }
  }

  @override
  Widget build(BuildContext context) {
    ref.listen<AsyncValue<Map<String, dynamic>>>(parentDashboardProvider, (previous, next) {
      if (next.hasValue && next.value != null) {
        final nextData = next.value!;
        final prevData = previous?.value;

        // 1. Check for new notifications
        final nextNotifs = (nextData['notifications'] as List?) ?? [];
        final prevNotifs = (prevData?['notifications'] as List?) ?? [];
        if (prevNotifs.isNotEmpty && nextNotifs.length > prevNotifs.length) {
          final newNotif = nextNotifs.first;
          NotificationHelper.showNotification(
            newNotif['title'] ?? 'New Notification',
            newNotif['message'] ?? '',
          );
        }

        // 2. Check for new upcoming events
        final nextEvents = (nextData['upcomingEvents'] as List?) ?? [];
        final prevEvents = (prevData?['upcomingEvents'] as List?) ?? [];
        if (prevEvents.isNotEmpty && nextEvents.length > prevEvents.length) {
          final prevIds = prevEvents.map((e) => e['id']).toSet();
          final newEvent = nextEvents.firstWhere((e) => !prevIds.contains(e['id']), orElse: () => null);
          if (newEvent != null) {
            NotificationHelper.showNotification(
              'New Upcoming Event',
              '${newEvent['title']}: ${newEvent['description'] ?? ""}',
            );
          }
        }
      }
    });

    final dashboardAsync = ref.watch(parentDashboardProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('EduFlow Parent'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_active),
            onPressed: () {
              // Show notifications
              _showNotificationsSheet(context);
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.go('/settings'),
          ),
        ],
      ),
      body: dashboardAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.cloud_off, size: 48, color: Colors.grey),
                const SizedBox(height: 16),
                Text('Failed to load data', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                Text('$err', style: const TextStyle(color: Colors.grey, fontSize: 12), textAlign: TextAlign.center),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => ref.invalidate(parentDashboardProvider),
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
        data: (data) {
          final student = data['student'] ?? {};
          final todayTimetable = (data['todayTimetable'] as List?) ?? [];
          final liveClass = _getCurrentLiveClass(todayTimetable);
          final upcomingEvents = (data['upcomingEvents'] as List?) ?? [];
          final notifications = (data['notifications'] as List?) ?? [];

          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(parentDashboardProvider),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // 1. Greeting
                  Text('${_getGreeting()}, ${(student['name'] ?? 'Parent').toString().split(' ').first}',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(
                    '${student['branch'] ?? ''} - ${student['semester'] ?? ''} (${student['roll_number'] ?? ''})',
                    style: const TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 24),

                  // 2. Live Status
                  if (liveClass != null)
                    _buildLiveClassCard(context, (student['name'] ?? 'Student').toString(), liveClass)
                  else
                    _buildNoLiveClassCard(context, (student['name'] ?? 'Student').toString()),

                  const SizedBox(height: 24),

                  // 3. Academic KPIs
                  Row(
                    children: [
                      Expanded(child: _buildKpiCard(context, 'Attendance %', '${data['attendancePercentage'] ?? 0}%', Colors.green, Icons.check_circle)),
                      const SizedBox(width: 16),
                      Expanded(child: _buildKpiCard(context, 'Current CGPA', '${data['examSummary']?['gpa'] ?? 'N/A'}', Colors.blue, Icons.grade)),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // 4. AI Insight Card
                  if (data['aiInsights'] != null)
                    _buildAiInsightCard(context, data['aiInsights']['message'] ?? ''),
                  const SizedBox(height: 32),

                  // 5. Upcoming Events (REAL from DB)
                  Text('Upcoming Events', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  if (upcomingEvents.isEmpty)
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Theme.of(context).cardColor,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.withOpacity(0.1)),
                      ),
                      child: const Text('No upcoming events.', style: TextStyle(color: Colors.grey), textAlign: TextAlign.center),
                    )
                  else
                    ...upcomingEvents.map<Widget>((evt) => _buildAgendaItem(
                          context,
                          evt['title'] ?? 'Event',
                          '${_getRelativeDate(evt['date'] ?? '')}${evt['description'] != null && evt['description'].toString().isNotEmpty ? ' • ${evt['description']}' : ''}',
                          Icons.event,
                          Colors.purple,
                        )),
                  const SizedBox(height: 32),

                  // 6. Today's Timetable
                  Text("Today's Schedule", style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  if (todayTimetable.isEmpty || todayTimetable[0]['subject'] == 'No classes scheduled today')
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Theme.of(context).cardColor,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.withOpacity(0.1)),
                      ),
                      child: const Text('No classes scheduled today.', style: TextStyle(color: Colors.grey), textAlign: TextAlign.center),
                    )
                  else
                    ...todayTimetable.map<Widget>((tt) => _buildAgendaItem(
                          context,
                          '${tt['subject']}',
                          '${tt['time'] ?? ''} • Prof. ${tt['faculty'] ?? ''}',
                          Icons.book,
                          tt == liveClass ? Colors.green : Colors.indigo,
                        )),
                  const SizedBox(height: 32),

                  // 7. Quick Actions
                  Text('Quick Actions', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 3,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    children: [
                      _buildGridAction(context, 'Settings', Icons.settings, Colors.blueGrey, onTap: () => context.go('/settings')),
                      _buildGridAction(context, 'Faculty Contact', Icons.support_agent, Colors.indigo),
                      _buildGridAction(context, 'Leave Request', Icons.edit_calendar, Colors.teal),
                    ],
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  void _showNotificationsSheet(BuildContext context) {
    final dashboardData = ref.read(parentDashboardProvider);
    dashboardData.whenData((data) {
      final notifications = (data['notifications'] as List?) ?? [];
      showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
        builder: (ctx) => DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.5,
          minChildSize: 0.3,
          maxChildSize: 0.8,
          builder: (_, scrollController) => Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(child: Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2)))),
                const SizedBox(height: 16),
                Text('Notifications', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                if (notifications.isEmpty)
                  const Expanded(child: Center(child: Text('No notifications yet.', style: TextStyle(color: Colors.grey))))
                else
                  Expanded(
                    child: ListView.builder(
                      controller: scrollController,
                      itemCount: notifications.length,
                      itemBuilder: (_, i) {
                        final n = notifications[i];
                        return ListTile(
                          leading: const CircleAvatar(child: Icon(Icons.notifications, size: 20)),
                          title: Text(n['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                          subtitle: Text(n['message'] ?? '', style: const TextStyle(fontSize: 12)),
                          trailing: Text(n['date'] ?? '', style: const TextStyle(fontSize: 10, color: Colors.grey)),
                        );
                      },
                    ),
                  ),
              ],
            ),
          ),
        ),
      );
    });
  }

  Widget _buildLiveClassCard(BuildContext context, String studentName, Map<String, dynamic> liveClass) {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF1E3A8A), Color(0xFF3B82F6)]),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: Colors.blue.withOpacity(0.3), blurRadius: 10, offset: const Offset(0, 5))],
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(color: Colors.redAccent, borderRadius: BorderRadius.circular(12)),
                child: const Row(
                  children: [
                    Icon(Icons.circle, color: Colors.white, size: 8),
                    SizedBox(width: 4),
                    Text('LIVE NOW', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
              const Spacer(),
              const Icon(Icons.access_time, color: Colors.white70, size: 16),
              const SizedBox(width: 4),
              Text(liveClass['time'] ?? '', style: const TextStyle(color: Colors.white70, fontSize: 12)),
            ],
          ),
          const SizedBox(height: 16),
          Text('${studentName.split(" ")[0]} is currently attending', style: const TextStyle(color: Colors.white70, fontSize: 14)),
          const SizedBox(height: 4),
          Text(liveClass['subject'] ?? '', style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text('with Prof. ${liveClass['faculty'] ?? ''}', style: const TextStyle(color: Colors.white, fontSize: 16)),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(color: Colors.white.withOpacity(0.15), borderRadius: BorderRadius.circular(12)),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("Today's Attendance", style: TextStyle(color: Colors.white, fontWeight: FontWeight.w500)),
                Text('Marked (Present)', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNoLiveClassCard(BuildContext context, String studentName) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey.shade300),
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.coffee, color: Colors.grey, size: 20),
              SizedBox(width: 8),
              Text('Free Period / Break', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 16),
          Text("${studentName.split(' ')[0]} doesn't have any class going on right now.", style: const TextStyle(color: Colors.black54, fontSize: 14)),
        ],
      ),
    );
  }

  Widget _buildKpiCard(BuildContext context, String title, String value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 12),
          Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: color)),
          const SizedBox(height: 4),
          Text(title, style: const TextStyle(fontSize: 12, color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _buildAiInsightCard(BuildContext context, String message) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.purple.withOpacity(0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.purple.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: Colors.purple.withOpacity(0.1), shape: BoxShape.circle),
            child: const Icon(Icons.auto_awesome, color: Colors.purple),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('EduFlow AI Insight', style: TextStyle(color: Colors.purple, fontWeight: FontWeight.bold, fontSize: 12)),
                const SizedBox(height: 4),
                Text(message, style: const TextStyle(color: Colors.black87, fontSize: 14)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAgendaItem(BuildContext context, String title, String subtitle, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.withOpacity(0.1)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(10)),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(subtitle, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGridAction(BuildContext context, String title, IconData icon, Color color, {VoidCallback? onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 28),
          ),
          const SizedBox(height: 8),
          Text(title, textAlign: TextAlign.center, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
