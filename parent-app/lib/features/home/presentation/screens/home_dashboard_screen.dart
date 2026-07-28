import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:go_router/go_router.dart';
import 'dart:async';

// State provider for Academic Session Switcher
final selectedSessionIdProvider = StateProvider<int?>((ref) => null);

// Provide the dashboard data with term switching capabilities
final parentDashboardProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final dioClient = ref.watch(dioClientProvider);
  final sessionId = ref.watch(selectedSessionIdProvider);
  
  String url = '/parent/dashboard';
  if (sessionId != null) {
    url += '?session_id=$sessionId';
  }
  
  final response = await dioClient.dio.get(url);
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
    final selectedSession = ref.watch(selectedSessionIdProvider);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('EduFlow Parent Portal', style: TextStyle(fontWeight: FontWeight.bold)),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () => context.push('/notifications'),
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
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () => ref.invalidate(parentDashboardProvider),
                child: const Text('Retry Synchronizing'),
              )
            ],
          ),
        ),
        data: (data) {
          final student = data['studentStatus'] ?? {};
          final todaySummary = student['today_summary'] ?? data['todaySummary'] ?? {};
          final stats = data['quickStats'] ?? {};
          final ai = data['aiInsights'] ?? {};
          final timeline = data['timeline'] as List? ?? [];
          final academic = data['academicPerformance'] as List? ?? [];
          final subjectWise = data['subjectWiseAttendance'] as List? ?? [];
          final comments = data['facultyComments'] as List? ?? [];
          
          final sessionInfo = data['session_info'] ?? {};
          final List availableSessions = sessionInfo['available_sessions'] as List? ?? [];
          final int? currentSessionId = sessionInfo['active_session_id'];

          final double attendancePct = (stats['attendance_percentage'] ?? 100.0).toDouble();
          final bool isShortage = attendancePct < 75.0;

          final bool isCompletedOrFree = student['current_status'] == 'FREE' || todaySummary['is_completed'] == true;

          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(parentDashboardProvider),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // --- Header & Academic Term Switcher ---
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('${_getGreeting()}, Parent', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                            const SizedBox(height: 4),
                            Text('${student['name']} | Roll: ${student['roll_number']}', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey[700], fontWeight: FontWeight.w600)),
                          ],
                        ),
                      ),
                      if (availableSessions.isNotEmpty)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFEFF6FF),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: const Color(0xFFBFDBFE)),
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<int>(
                              value: selectedSession ?? currentSessionId,
                              icon: const Icon(Icons.calendar_month, size: 16, color: Color(0xFF2563EB)),
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF1E40AF)),
                              onChanged: (newSessionId) {
                                ref.read(selectedSessionIdProvider.notifier).state = newSessionId;
                              },
                              items: availableSessions.map<DropdownMenuItem<int>>((s) {
                                return DropdownMenuItem<int>(
                                  value: s['id'],
                                  child: Text('${s['semester']}', style: const TextStyle(fontSize: 12)),
                                );
                              }).toList(),
                            ),
                          ),
                        ),
                    ],
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // --- Intelligent Blue Status / Today's Summary Card ---
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(22),
                    decoration: BoxDecoration(
                      gradient: isCompletedOrFree
                          ? const LinearGradient(
                              colors: [Color(0xFF1E3A8A), Color(0xFF4F46E5)],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            )
                          : const LinearGradient(
                              colors: [Color(0xFF2563EB), Color(0xFF7C3AED)],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            ),
                      borderRadius: BorderRadius.circular(24),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF2563EB).withOpacity(0.35),
                          blurRadius: 18,
                          offset: const Offset(0, 8),
                        )
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                              decoration: BoxDecoration(
                                color: isCompletedOrFree ? Colors.white.withOpacity(0.2) : Colors.redAccent,
                                borderRadius: BorderRadius.circular(16),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    isCompletedOrFree ? Icons.done_all : Icons.circle,
                                    size: 12,
                                    color: Colors.white,
                                  ),
                                  const SizedBox(width: 6),
                                  Text(
                                    isCompletedOrFree ? 'TODAY\'S SUMMARY' : 'LIVE NOW',
                                    style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.5),
                                  ),
                                ],
                              ),
                            ),
                            if (!isCompletedOrFree)
                              Row(
                                children: [
                                  const Icon(Icons.location_on, color: Colors.white70, size: 16),
                                  const SizedBox(width: 4),
                                  Text(student['current_room'] ?? 'Campus', style: const TextStyle(color: Colors.white70, fontWeight: FontWeight.w600, fontSize: 13)),
                                ],
                              ),
                          ],
                        ),
                        const SizedBox(height: 18),
                        if (isCompletedOrFree) ...[
                          Text(
                            todaySummary['heading'] ?? "Today's Summary",
                            style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.w900),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            todaySummary['attendance_fraction'] ?? "Daily classes concluded",
                            style: const TextStyle(color: Colors.white70, fontSize: 15, fontWeight: FontWeight.w500),
                          ),
                          const SizedBox(height: 16),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.12),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: Colors.white.withOpacity(0.2)),
                            ),
                            child: Row(
                              children: [
                                const Icon(Icons.event_available, color: Color(0xFF93C5FD), size: 18),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    'Next Event: ${todaySummary['next_event'] ?? "No upcoming events scheduled"}',
                                    style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w600),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ] else ...[
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.baseline,
                            textBaseline: TextBaseline.alphabetic,
                            children: [
                              Text(
                                student['current_subject'] ?? 'Live Session',
                                style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.w900),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                '(${student['current_subject_code'] ?? "--"})',
                                style: const TextStyle(color: Color(0xFF93C5FD), fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Faculty: ${student['current_faculty'] ?? "--"} | Attendance Tracking Active',
                            style: const TextStyle(color: Colors.white70, fontSize: 14, fontWeight: FontWeight.w500),
                          ),
                        ],
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // --- Quick Stats Row ---
                  Row(
                    children: [
                      Expanded(child: _StatCard(title: 'Attendance', value: '$attendancePct%', icon: Icons.check_circle, color: isShortage ? const Color(0xFFEF4444) : const Color(0xFF10B981))),
                      const SizedBox(width: 12),
                      Expanded(child: _StatCard(title: 'CGPA', value: '${stats['cgpa'] ?? 0}', icon: Icons.star, color: const Color(0xFFF59E0B))),
                      const SizedBox(width: 12),
                      Expanded(child: _StatCard(title: 'Credits', value: '${stats['credits_earned'] ?? 0}', icon: Icons.school, color: const Color(0xFF4F46E5))),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // --- Overall Attendance Health & Statutory Alert ---
                  Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: isShortage ? const Color(0xFFFEF2F2) : const Color(0xFFECFDF5),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: isShortage ? const Color(0xFFFECACA) : const Color(0xFFA7F3D0)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  isShortage ? Icons.warning_amber_rounded : Icons.verified_user,
                                  color: isShortage ? const Color(0xFFDC2626) : const Color(0xFF059669),
                                  size: 22,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Overall Attendance Health ($attendancePct%)',
                                  style: TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.bold,
                                    color: isShortage ? const Color(0xFF991B1B) : const Color(0xFF065F46),
                                  ),
                                ),
                              ],
                            ),
                            Text(
                              isShortage ? 'SHORTAGE (<75%)' : 'GOOD STATUS',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w800,
                                color: isShortage ? const Color(0xFFDC2626) : const Color(0xFF059669),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: LinearProgressIndicator(
                            value: (attendancePct / 100).clamp(0.0, 1.0),
                            backgroundColor: isShortage ? const Color(0xFFFEE2E2) : const Color(0xFFD1FAE5),
                            color: isShortage ? const Color(0xFFDC2626) : const Color(0xFF10B981),
                            minHeight: 10,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          isShortage
                              ? '⚠️ ATTENTION: Overall attendance is below the university 75% statutory requirement. Immediate parental counseling advised.'
                              : '✓ PERFECT: Overall attendance exceeds statutory university minimums.',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: isShortage ? const Color(0xFFB91C1C) : const Color(0xFF047857),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 28),

                  // --- AI Insight ---
                  _SectionHeader(title: 'EduFlow Executive AI Insight', icon: Icons.auto_awesome),
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
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  ai['trend'] ?? 'Diagnostic Narrative',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF4F46E5)),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  ai['message'] ?? 'Gathering live AI insights...',
                                  style: const TextStyle(height: 1.5, color: Colors.black87, fontSize: 13),
                                ),
                              ],
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

                  // --- Detailed Subject-Wise Attendance Breakdown ---
                  _SectionHeader(title: 'Subject-Wise Attendance Ledger', icon: Icons.menu_book),
                  const SizedBox(height: 14),
                  if (subjectWise.isEmpty)
                    Container(
                      padding: const EdgeInsets.all(20),
                      alignment: Alignment.center,
                      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: Colors.grey[200]!)),
                      child: const Text('No active course attendance logged for this term.', style: TextStyle(color: Colors.grey, fontSize: 13)),
                    )
                  else
                    ...subjectWise.map((item) => _SubjectAttendanceCard(
                          subjectName: item['subject_name'] ?? 'Subject',
                          subjectCode: item['subject_code'] ?? 'SUB',
                          totalClasses: item['total_classes'] ?? 0,
                          attendedClasses: item['total_present'] ?? 0,
                          percentage: (item['percentage'] ?? 100.0).toDouble(),
                        )),

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
                  ...academic.map((s) => _SubjectProgress(subject: "${s['subject']} (${s['subject_code'] ?? ''})", marks: s['marks'], grade: s['grade'])),

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
                              Expanded(child: Text(c['comment'], style: const TextStyle(color: Colors.black87, fontSize: 12), maxLines: 3, overflow: TextOverflow.ellipsis)),
                            ],
                          ),
                        );
                      }
                    ),
                  ),
                  
                  const SizedBox(height: 40),
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
          Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
          const SizedBox(height: 4),
          Text(title, style: TextStyle(fontSize: 12, color: Colors.grey[600], fontWeight: FontWeight.w600)),
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
      borderRadius: BorderRadius.circular(14),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE5E7EB)),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 6)],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 18, color: const Color(0xFF4F46E5)),
            const SizedBox(width: 8),
            Text(label, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
          ],
        ),
      ),
    );
  }
}

class _SubjectAttendanceCard extends StatelessWidget {
  final String subjectName;
  final String subjectCode;
  final int totalClasses;
  final int attendedClasses;
  final double percentage;

  const _SubjectAttendanceCard({
    required this.subjectName,
    required this.subjectCode,
    required this.totalClasses,
    required this.attendedClasses,
    required this.percentage,
  });

  @override
  Widget build(BuildContext context) {
    final bool isLow = percentage < 75.0;
    final Color tintColor = isLow ? const Color(0xFFEF4444) : const Color(0xFF10B981);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: isLow ? const Color(0xFFFECACA) : const Color(0xFFE5E7EB)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 8)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  '$subjectName ($subjectCode)',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF1F2937)),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: tintColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '$percentage%',
                  style: TextStyle(color: tintColor, fontWeight: FontWeight.w800, fontSize: 12),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: LinearProgressIndicator(
                    value: (percentage / 100).clamp(0.0, 1.0),
                    backgroundColor: Colors.grey[200],
                    color: tintColor,
                    minHeight: 6,
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Text(
                '$attendedClasses / $totalClasses Attended',
                style: TextStyle(color: Colors.grey[600], fontSize: 12, fontWeight: FontWeight.w600),
              ),
            ],
          ),
        ],
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
            width: 65,
            child: Text(time, style: TextStyle(color: Colors.grey[600], fontSize: 12, fontWeight: FontWeight.w600)),
          ),
          Column(
            children: [
              Container(width: 12, height: 12, decoration: BoxDecoration(color: dotColor, shape: BoxShape.circle, border: Border.all(color: Colors.white, width: 2))),
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
                  Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                  const SizedBox(height: 4),
                  Text(desc, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
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
            child: Text(subject, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
          ),
          Expanded(
            flex: 3,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: (marks / 100).clamp(0.0, 1.0),
                backgroundColor: const Color(0xFFE5E7EB),
                color: marks > 80 ? const Color(0xFF10B981) : (marks > 60 ? const Color(0xFFF59E0B) : const Color(0xFFEF4444)),
                minHeight: 8,
              ),
            ),
          ),
          const SizedBox(width: 16),
          SizedBox(
            width: 45,
            child: Text(
              '$marks ($grade)', 
              textAlign: TextAlign.right, 
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)
            ),
          )
        ],
      ),
    );
  }
}
