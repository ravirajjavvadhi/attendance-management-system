import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:go_router/go_router.dart';

class NotificationCenterScreen extends ConsumerWidget {
  const NotificationCenterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // In a real implementation, we'd watch a provider for notifications.
    // For now, we fetch from the dashboard provider or mock them if empty.
    
    // We'll use mock data to demonstrate the premium UI.
    final notifications = [
      {
        "id": 1,
        "title": "Attendance Alert",
        "message": "Absent Alert: AFTAR (24AG1A05J4) was absent for Physics (Period 1) on 2026-07-20.",
        "date": "2026-07-20 09:15",
        "type": "ATTENDANCE",
        "isRead": false,
      },
      {
        "id": 2,
        "title": "Fee Reminder",
        "message": "Semester 2 fees are due by 2026-08-01. Please pay to avoid late fees.",
        "date": "2026-07-15 10:00",
        "type": "FEES",
        "isRead": true,
      },
      {
        "id": 3,
        "title": "New Assignment",
        "message": "Calculus Assignment 1 has been posted by Dr. Kumar.",
        "date": "2026-07-14 14:30",
        "type": "ACADEMIC",
        "isRead": true,
      }
    ];

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        title: const Text('Notification Center', style: TextStyle(fontWeight: FontWeight.bold)),
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
                tabs: [
                  Tab(text: 'All'),
                  Tab(text: 'Unread'),
                  Tab(text: 'Academic'),
                ],
              ),
            ),
            Expanded(
              child: TabBarView(
                children: [
                  _NotificationList(notifications: notifications),
                  _NotificationList(notifications: notifications.where((n) => !(n['isRead'] as bool)).toList()),
                  _NotificationList(notifications: notifications.where((n) => n['type'] == 'ACADEMIC').toList()),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _NotificationList extends StatelessWidget {
  final List<Map<String, dynamic>> notifications;

  const _NotificationList({required this.notifications});

  @override
  Widget build(BuildContext context) {
    if (notifications.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.notifications_off, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text('No notifications', style: TextStyle(color: Colors.grey[600], fontSize: 16)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: notifications.length,
      itemBuilder: (context, index) {
        final notif = notifications[index];
        final isRead = notif['isRead'] as bool;
        
        IconData icon = Icons.notifications;
        Color iconColor = const Color(0xFF2563EB);
        if (notif['type'] == 'ATTENDANCE') {
          icon = Icons.warning_rounded;
          iconColor = const Color(0xFFEF4444);
        } else if (notif['type'] == 'FEES') {
          icon = Icons.payments;
          iconColor = const Color(0xFFF59E0B);
        } else if (notif['type'] == 'ACADEMIC') {
          icon = Icons.school;
          iconColor = const Color(0xFF10B981);
        }

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isRead ? Colors.white : const Color(0xFFF0F9FF),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: isRead ? const Color(0xFFE5E7EB) : const Color(0xFFBAE6FD)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: iconColor, size: 20),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(notif['title'], style: TextStyle(fontWeight: isRead ? FontWeight.w500 : FontWeight.bold, fontSize: 16)),
                        Text(notif['date'].split(' ')[0], style: TextStyle(color: Colors.grey[500], fontSize: 12)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      notif['message'],
                      style: TextStyle(color: Colors.grey[700], height: 1.4),
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
