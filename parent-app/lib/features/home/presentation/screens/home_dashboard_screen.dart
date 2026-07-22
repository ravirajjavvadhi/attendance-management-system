import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:go_router/go_router.dart';
import 'dart:async';

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
    _refreshTimer = Timer.periodic(const Duration(seconds: 60), (_) {
      ref.invalidate(parentDashboardProvider);
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  }

  @override
  Widget build(BuildContext context) {
    final dashboardAsync = ref.watch(parentDashboardProvider);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('EduFlow Parent', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () => context.push('/notifications'), // Go to Notification Center
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: dashboardAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.redAccent),
              const SizedBox(height: 16),
              Text('Error loading dashboard: $err'),
              ElevatedButton(
                onPressed: () => ref.invalidate(parentDashboardProvider),
                child: const Text('Retry'),
              )
            ],
          ),
        ),
        data: (data) {
          final student = data['studentStatus'] ?? {};
          final stats = data['quickStats'] ?? {};
          final ai = data['aiInsights'] ?? {};
          final timeline = data['timeline'] as List? ?? [];
          final academic = data['academicPerformance'] as List? ?? [];
          final comments = data['facultyComments'] as List? ?? [];

          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(parentDashboardProvider),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // --- Header & Student Status ---
                  Text('${_getGreeting()}, Parent', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text('${student['name']} | ${student['roll_number']}', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey[700])),
                  
                  const SizedBox(height: 24),
                  
                  // Live Status Card (Glassmorphism inspired)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF2563EB), Color(0xFF4F46E5)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [BoxShadow(color: const Color(0xFF2563EB).withOpacity(0.3), blurRadius: 15, offset: const Offset(0, 8))],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: student['current_status'] == 'LIVE NOW' ? Colors.redAccent : Colors.white24,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                student['current_status'] ?? 'N/A',
                                style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                              ),
                            ),
                            const Spacer(),
                            const Icon(Icons.location_on, color: Colors.white70, size: 16),
                            const SizedBox(width: 4),
                            Text(student['current_room'] ?? '', style: const TextStyle(color: Colors.white70)),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text(student['current_subject'] ?? 'No class currently', style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        Text('with ${student['current_faculty'] ?? ''}', style: const TextStyle(color: Colors.white70, fontSize: 14)),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // --- Quick Stats Row ---
                  Row(
                    children: [
                      Expanded(child: _StatCard(title: 'Attendance', value: '${stats['attendance_percentage'] ?? 0}%', icon: Icons.check_circle, color: const Color(0xFF10B981))),
                      const SizedBox(width: 12),
                      Expanded(child: _StatCard(title: 'CGPA', value: '${stats['cgpa'] ?? 0}', icon: Icons.star, color: const Color(0xFFF59E0B))),
                      const SizedBox(width: 12),
                      Expanded(child: _StatCard(title: 'Credits', value: '${stats['credits_earned'] ?? 0}', icon: Icons.school, color: const Color(0xFF4F46E5))),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // --- AI Insight ---
                  _SectionHeader(title: 'EduFlow AI Insight', icon: Icons.auto_awesome),
                  Card(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20), side: const BorderSide(color: Color(0xFFE5E7EB))),
                    elevation: 0,
                    margin: const EdgeInsets.only(top: 12),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(color: const Color(0xFF4F46E5).withOpacity(0.1), shape: BoxShape.circle),
                            child: const Icon(Icons.auto_awesome, color: Color(0xFF4F46E5)),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Text(
                              ai['message'] ?? 'Gathering insights...',
                              style: const TextStyle(height: 1.5, color: Colors.black87),
                            ),
                          )
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 32),

                  // --- Quick Actions ---
                  const Text('Quick Actions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      _QuickActionChip(icon: Icons.edit_document, label: 'Leave Request', onTap: () => context.push('/leave-request')),
                      _QuickActionChip(icon: Icons.payments, label: 'Pay Fees', onTap: () => context.push('/pay-fees')),
                      _QuickActionChip(icon: Icons.download, label: 'Documents', onTap: () => context.push('/documents')),
                      _QuickActionChip(icon: Icons.chat, label: 'Contact Faculty', onTap: () => context.push('/contact-faculty')),
                    ],
                  ),

                  const SizedBox(height: 32),

                  // --- Parent Timeline ---
                  _SectionHeader(title: 'Today\'s Timeline', icon: Icons.timeline),
                  const SizedBox(height: 16),
                  ...timeline.map((e) => _TimelineItem(
                    time: e['time'], 
                    title: e['title'], 
                    desc: e['description'], 
                    isLast: timeline.last == e,
                    type: e['type']
                  )),

                  const SizedBox(height: 32),

                  // --- Academic Performance ---
                  _SectionHeader(title: 'Academic Performance', icon: Icons.analytics),
                  const SizedBox(height: 16),
                  ...academic.map((s) => _SubjectProgress(subject: s['subject'], marks: s['marks'], grade: s['grade'])),

                  const SizedBox(height: 32),

                  // --- Faculty Comments ---
                  _SectionHeader(title: 'Faculty Remarks', icon: Icons.comment),
                  const SizedBox(height: 16),
                  SizedBox(
                    height: 120,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: comments.length,
                      itemBuilder: (context, index) {
                        final c = comments[index];
                        return Container(
                          width: 280,
                          margin: const EdgeInsets.only(right: 16),
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: const Color(0xFFE5E7EB)),
                            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10)],
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(c['faculty_name'], style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF2563EB))),
                              const SizedBox(height: 8),
                              Expanded(child: Text(c['comment'], style: const TextStyle(color: Colors.black87), maxLines: 3, overflow: TextOverflow.ellipsis)),
                            ],
                          ),
                        );
                      }
                    ),
                  ),
                  
                  const SizedBox(height: 40), // Bottom padding
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

// --- Helper Widgets ---

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _StatCard({required this.title, required this.value, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE5E7EB)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 12),
          Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(title, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  final IconData icon;

  const _SectionHeader({required this.title, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: const Color(0xFF2563EB)),
        const SizedBox(width: 8),
        Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      ],
    );
  }
}

class _QuickActionChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onTap;

  const _QuickActionChip({required this.icon, required this.label, this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap ?? () {},
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE5E7EB)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 18, color: const Color(0xFF4F46E5)),
            const SizedBox(width: 8),
            Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }
}

class _TimelineItem extends StatelessWidget {
  final String time;
  final String title;
  final String desc;
  final bool isLast;
  final String type;

  const _TimelineItem({required this.time, required this.title, required this.desc, required this.isLast, required this.type});

  @override
  Widget build(BuildContext context) {
    Color dotColor = const Color(0xFF2563EB);
    String upperType = type.toUpperCase();
    if (upperType.contains('ABSENT')) dotColor = const Color(0xFFEF4444);
    if (upperType.contains('PRESENT')) dotColor = const Color(0xFF10B981);

    return IntrinsicHeight(
      child: Row(
        children: [
          SizedBox(
            width: 60,
            child: Text(time, style: TextStyle(color: Colors.grey[600], fontSize: 12, fontWeight: FontWeight.w500)),
          ),
          Column(
            children: [
              Container(width: 12, height: 12, decoration: BoxDecoration(color: dotColor, shape: BoxShape.circle)),
              if (!isLast) Expanded(child: Container(width: 2, color: const Color(0xFFE5E7EB))),
            ],
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(bottom: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  const SizedBox(height: 4),
                  Text(desc, style: TextStyle(color: Colors.grey[600], fontSize: 13)),
                ],
              ),
            ),
          )
        ],
      ),
    );
  }
}

class _SubjectProgress extends StatelessWidget {
  final String subject;
  final int marks;
  final String grade;

  const _SubjectProgress({required this.subject, required this.marks, required this.grade});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(subject, style: const TextStyle(fontWeight: FontWeight.w500)),
          ),
          Expanded(
            flex: 3,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: marks / 100,
                backgroundColor: const Color(0xFFE5E7EB),
                color: marks > 80 ? const Color(0xFF10B981) : (marks > 60 ? const Color(0xFFF59E0B) : const Color(0xFFEF4444)),
                minHeight: 8,
              ),
            ),
          ),
          const SizedBox(width: 16),
          SizedBox(
            width: 40,
            child: Text(
              '$marks', 
              textAlign: TextAlign.right, 
              style: const TextStyle(fontWeight: FontWeight.bold)
            ),
          )
        ],
      ),
    );
  }
}
