import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:go_router/go_router.dart';
import 'package:eduflow_parent/features/home/presentation/screens/home_dashboard_screen.dart';

class NotificationCenterScreen extends ConsumerWidget {
  const NotificationCenterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardAsync = ref.watch(parentDashboardProvider);

    return dashboardAsync.when(
      loading: () => Scaffold(
        appBar: AppBar(title: const Text('Immutable Event Stream', style: TextStyle(fontWeight: FontWeight.bold))),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (e, st) => Scaffold(
        appBar: AppBar(title: const Text('Immutable Event Stream')),
        body: Center(child: Text('Error loading events: $e')),
      ),
      data: (data) {
        final List<dynamic> rawNotifs = data['notifications'] ?? [];
        final notifications = rawNotifs.map((e) => Map<String, dynamic>.from(e as Map)).toList();
        
        final attendanceNotifs = notifications.where((n) {
          final type = str(n['type'] ?? '').toUpperCase();
          final title = str(n['title'] ?? '').toLowerCase();
          final msg = str(n['message'] ?? '').toLowerCase();
          return type == 'ATTENDANCE' || title.contains('attendance') || title.contains('alert') || msg.contains('absent') || msg.contains('present');
        }).toList();
        
        final unreadNotifs = notifications.where((n) => !(n['isRead'] == true)).toList();

        return Scaffold(
          backgroundColor: Theme.of(context).scaffoldBackgroundColor,
          appBar: AppBar(
            leading: IconButton(
              icon: const Icon(Icons.arrow_back),
              onPressed: () => context.pop(),
            ),
            title: const Text('Notification & Event Stream', style: TextStyle(fontWeight: FontWeight.bold)),
            elevation: 0,
          ),
          body: DefaultTabController(
            length: 3,
            child: Column(
              children: [
                Container(
                  color: Theme.of(context).scaffoldBackgroundColor,
                  child: const TabBar(
                    labelColor: Color(0xFF2563EB),
                    unselectedLabelColor: Colors.grey,
                    indicatorColor: Color(0xFF2563EB),
                    indicatorWeight: 3,
                    labelStyle: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    tabs: [
                      Tab(text: 'All Events'),
                      Tab(text: 'Attendance Alerts'),
                      Tab(text: 'Unread Logs'),
                    ],
                  ),
                ),
                Expanded(
                  child: TabBarView(
                    children: [
                      _NotificationList(notifications: notifications, emptyLabel: 'No events logged in the immutable stream yet.'),
                      _NotificationList(notifications: attendanceNotifs, emptyLabel: 'No attendance absence warnings recorded.'),
                      _NotificationList(notifications: unreadNotifs, emptyLabel: 'All broadcast event notifications have been reviewed.'),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

String str(dynamic val) => val?.toString() ?? '';

class _NotificationList extends StatelessWidget {
  final List<Map<String, dynamic>> notifications;
  final String emptyLabel;

  const _NotificationList({required this.notifications, required this.emptyLabel});

  @override
  Widget build(BuildContext context) {
    if (notifications.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.verified_outlined, size: 56, color: Colors.grey[400]),
              ),
              const SizedBox(height: 18),
              Text(
                'Stream Status Quiet',
                style: TextStyle(color: Colors.grey[800], fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 6),
              Text(
                emptyLabel,
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey[600], fontSize: 13, height: 1.4),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: notifications.length,
      itemBuilder: (context, index) {
        final notif = notifications[index];
        final isRead = notif['isRead'] == true;
        final type = str(notif['type']).toUpperCase();
        final msg = str(notif['message']).toLowerCase();
        
        IconData icon = Icons.notifications_active_outlined;
        Color badgeColor = const Color(0xFF2563EB);
        String badgeText = "SYSTEM EVENT";

        if (type == 'ATTENDANCE' || msg.contains('absent')) {
          icon = Icons.warning_amber_rounded;
          badgeColor = const Color(0xFFEF4444);
          badgeText = "ATTENDANCE ALERT";
        } else if (type == 'FEES' || msg.contains('fee') || msg.contains('payment')) {
          icon = Icons.payments_outlined;
          badgeColor = const Color(0xFFF59E0B);
          badgeText = "FEE NOTICE";
        } else if (type == 'CIRCULAR' || msg.contains('welcome') || msg.contains('semester')) {
          icon = Icons.campaign_outlined;
          badgeColor = const Color(0xFF7C3AED);
          badgeText = "ACADEMIC CIRCULAR";
        } else if (type == 'ACADEMIC' || msg.contains('exam') || msg.contains('result')) {
          icon = Icons.school_outlined;
          badgeColor = const Color(0xFF10B981);
          badgeText = "CURRICULUM UPDATE";
        }

        return Container(
          margin: const EdgeInsets.only(bottom: 14),
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: isRead ? Colors.white : const Color(0xFFEFF6FF),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: isRead ? const Color(0xFFE5E7EB) : const Color(0xFFBFDBFE),
              width: isRead ? 1 : 1.5,
            ),
            boxShadow: [
              BoxShadow(
                color: badgeColor.withOpacity(0.04),
                blurRadius: 12,
                offset: const Offset(0, 4),
              )
            ],
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: badgeColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: badgeColor.withOpacity(0.2)),
                ),
                child: Icon(icon, color: badgeColor, size: 22),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2.5),
                          decoration: BoxDecoration(
                            color: badgeColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            badgeText,
                            style: TextStyle(color: badgeColor, fontSize: 10, fontWeight: FontWeight.w800, letterSpacing: 0.3),
                          ),
                        ),
                        Text(
                          str(notif['date']),
                          style: TextStyle(color: Colors.grey[500], fontSize: 11, fontWeight: FontWeight.w500),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      str(notif['title']),
                      style: TextStyle(
                        fontWeight: isRead ? FontWeight.w700 : FontWeight.w800,
                        fontSize: 15,
                        color: const Color(0xFF1E293B),
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      str(notif['message']),
                      style: TextStyle(color: Colors.grey[700], height: 1.4, fontSize: 13),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Icon(
                          isRead ? Icons.done : Icons.done_all,
                          size: 14,
                          color: isRead ? Colors.grey[400] : const Color(0xFF2563EB),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          isRead ? 'Archived via Event Stream' : 'New Broadcast Event',
                          style: TextStyle(
                            color: isRead ? Colors.grey[400] : const Color(0xFF2563EB),
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
