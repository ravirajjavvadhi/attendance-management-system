import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:intl/intl.dart';

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
  
  Map<String, dynamic>? _getCurrentLiveClass(List<dynamic> todayTimetable) {
    if (todayTimetable.isEmpty || todayTimetable[0]['subject'] == 'No classes scheduled today') {
      return null;
    }

    final now = DateTime.now();
    // Assuming time is in "09:00 - 10:00" format
    for (var tt in todayTimetable) {
      try {
        final timeStr = tt['time'] as String;
        final parts = timeStr.split('-');
        if (parts.length == 2) {
          final startTime = DateFormat("HH:mm").parse(parts[0].trim());
          final endTime = DateFormat("HH:mm").parse(parts[1].trim());

          final start = DateTime(now.year, now.month, now.day, startTime.hour, startTime.minute);
          final end = DateTime(now.year, now.month, now.day, endTime.hour, endTime.minute);

          if (now.isAfter(start) && now.isBefore(end)) {
            return tt;
          }
        }
      } catch (e) {
        // Parse error, ignore
      }
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final dashboardAsync = ref.watch(parentDashboardProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('EduFlow Parent'),
        actions: [
          IconButton(icon: const Icon(Icons.notifications_active), onPressed: () {}),
          IconButton(icon: const Icon(Icons.settings), onPressed: () {}),
        ],
      ),
      body: dashboardAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(child: Text('Failed to load data\n$err')),
        data: (data) {
          final student = data['student'];
          final liveClass = _getCurrentLiveClass(data['todayTimetable']);

          return SingleChildScrollView(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 1. Live Status Header
                Text('Monitoring ${student['name']}', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text('${student['branch']} - ${student['semester']} (${student['roll_number']})', style: const TextStyle(color: Colors.grey)),
                const SizedBox(height: 24),
                
                if (liveClass != null) 
                  _buildLiveClassCard(context, student['name'], liveClass)
                else
                  _buildNoLiveClassCard(context, student['name']),

                const SizedBox(height: 24),
                
                // 2. Academic KPIs
                Row(
                  children: [
                    Expanded(child: _buildKpiCard(context, 'Attendance %', '${data['attendancePercentage']}%', Colors.green, Icons.check_circle)),
                    const SizedBox(width: 16),
                    Expanded(child: _buildKpiCard(context, 'Current CGPA', '${data['examSummary']['gpa']}', Colors.blue, Icons.grade)),
                  ],
                ),
                const SizedBox(height: 24),
                
                // 3. AI Insight Card
                _buildAiInsightCard(context, data['aiInsights']['message']),
                const SizedBox(height: 32),
                
                // 4. Today's Timetable
                Text('Today\'s Schedule', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                ...List.generate(data['todayTimetable'].length, (index) {
                  final tt = data['todayTimetable'][index];
                  if (tt['subject'] == 'No classes scheduled today') {
                    return const Padding(padding: EdgeInsets.all(16.0), child: Text("No classes scheduled today", style: TextStyle(color: Colors.grey)));
                  }
                  return _buildAgendaItem(
                    context, 
                    '${tt['subject']}', 
                    '${tt['time']} • Prof. ${tt['faculty']}', 
                    Icons.book, 
                    Colors.indigo
                  );
                }),
                const SizedBox(height: 32),
                
                // 5. Timeline & Modules Grid
                Text('Quick Actions', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                GridView.count(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisCount: 3,
                  mainAxisSpacing: 16,
                  crossAxisSpacing: 16,
                  children: [
                    _buildGridAction(context, 'Faculty Contact', Icons.support_agent, Colors.indigo),
                    _buildGridAction(context, 'Leave Request', Icons.edit_calendar, Colors.teal),
                  ],
                ),
              ],
            ),
          );
        }
      ),
    );
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
              Text(liveClass['time'], style: const TextStyle(color: Colors.white70, fontSize: 12)),
            ],
          ),
          const SizedBox(height: 16),
          Text('${studentName.split(" ")[0]} is currently attending', style: const TextStyle(color: Colors.white70, fontSize: 14)),
          const SizedBox(height: 4),
          Text(liveClass['subject'], style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text('with Prof. ${liveClass['faculty']}', style: const TextStyle(color: Colors.white, fontSize: 16)),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(color: Colors.white.withOpacity(0.15), borderRadius: BorderRadius.circular(12)),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Today\'s Attendance', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w500)),
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
          Row(
            children: [
              const Icon(Icons.coffee, color: Colors.grey, size: 20),
              const SizedBox(width: 8),
              const Text('Free Period / Break', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 16),
          Text('${studentName.split(" ")[0]} doesn\'t have any class going on right now.', style: const TextStyle(color: Colors.black54, fontSize: 14)),
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

  Widget _buildAgendaItem(BuildContext context, String title, String time, IconData icon, Color color) {
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
                  Text(time, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGridAction(BuildContext context, String title, IconData icon, Color color) {
    return Column(
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
    );
  }
}
