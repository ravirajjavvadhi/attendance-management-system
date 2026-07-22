import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:dio/dio.dart';
import 'package:go_router/go_router.dart';

class FacultyDashboardScreen extends ConsumerStatefulWidget {
  const FacultyDashboardScreen({super.key});

  @override
  ConsumerState<FacultyDashboardScreen> createState() => _FacultyDashboardScreenState();
}

class _FacultyDashboardScreenState extends ConsumerState<FacultyDashboardScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  bool isLoading = true;
  String currentDay = "MONDAY";
  Map<String, List<dynamic>> weeklySchedule = {};
  List<dynamic> allSections = [];
  
  // Manual Override State
  String? manualSectionId;
  int manualPeriod = 1;

  final List<String> days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 6, vsync: this);
    _fetchDashboardData();
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchDashboardData() async {
    setState(() => isLoading = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      
      // Fetch schedule
      final schedRes = await dio.get('/academic/faculty/weekly-schedule');
      final data = schedRes.data;
      
      // Fetch sections for manual override
      final secRes = await dio.get('/academic/sections');
      
      if (mounted) {
        setState(() {
          currentDay = data['current_day'] ?? 'MONDAY';
          
          // Initialize schedule map
          final schedMap = data['schedule'] as Map<String, dynamic>;
          for (var day in days) {
            weeklySchedule[day] = schedMap[day] ?? [];
          }
          
          allSections = secRes.data;
          if (allSections.isNotEmpty) {
            manualSectionId = allSections[0]['id'].toString();
          }
          
          // Set initial tab to current day
          int todayIndex = days.indexOf(currentDay);
          if (todayIndex != -1) {
            _tabController.index = todayIndex;
          }
          
          isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load dashboard: $e')),
        );
      }
    }
  }

  void _navigateToAttendance(Map<String, dynamic> classData) {
    context.pushNamed('attendance', extra: {
      'sectionId': classData['section_id'].toString(),
      'periodNumber': classData['period_number'],
      'subjectName': classData['subject_name'],
      'classDetails': '${classData['department_name']} • ${classData['year_name']} • Section ${classData['section_name']}',
      'timeStr': classData['time'],
    });
  }

  void _navigateToManualAttendance() {
    if (manualSectionId == null) return;
    final sec = allSections.firstWhere((s) => s['id'].toString() == manualSectionId, orElse: () => {'name': 'Unknown'});
    
    context.pushNamed('attendance', extra: {
      'sectionId': manualSectionId,
      'periodNumber': manualPeriod,
      'subjectName': 'Manual Override',
      'classDetails': 'Section ${sec['name']}',
      'timeStr': 'Manual Entry',
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Faculty Schedule'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _fetchDashboardData,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: const Color(0xFF2563EB),
          unselectedLabelColor: Colors.grey,
          indicatorColor: const Color(0xFF2563EB),
          tabs: days.map((d) => Tab(text: d.substring(0, 3))).toList(),
        ),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: days.map((day) => _buildDayView(day)).toList(),
            ),
    );
  }

  Widget _buildDayView(String day) {
    final classes = weeklySchedule[day] ?? [];
    final isToday = day == currentDay;

    return RefreshIndicator(
      onRefresh: _fetchDashboardData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (isToday) ...[
            const Text(
              "Today's Classes",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 16),
          ],
          
          if (classes.isEmpty)
            Container(
              padding: const EdgeInsets.all(32),
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: Column(
                children: [
                  Icon(Icons.coffee_rounded, size: 48, color: Colors.grey[500]),
                  const SizedBox(height: 16),
                  const Text('Free Day!', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text('You have no classes scheduled.', style: TextStyle(color: Colors.grey[400], fontSize: 14)),
                ],
              ),
            )
          else
            ...classes.map((cls) => _buildClassCard(cls, isToday)),

          const SizedBox(height: 32),
          
          // Manual Override Accordion
          Theme(
            data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
            child: ExpansionTile(
              title: const Text('Manual Override / Cover Class', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
              collapsedBackgroundColor: Colors.grey.withOpacity(0.05),
              backgroundColor: Colors.transparent,
              tilePadding: const EdgeInsets.symmetric(horizontal: 16),
              childrenPadding: const EdgeInsets.all(16),
              children: [
                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        value: manualSectionId,
                        decoration: const InputDecoration(labelText: 'Select Section', border: OutlineInputBorder()),
                        items: allSections.map<DropdownMenuItem<String>>((s) {
                          return DropdownMenuItem<String>(
                            value: s['id'].toString(),
                            child: Text(s['name'] ?? 'Section'),
                          );
                        }).toList(),
                        onChanged: (val) => setState(() => manualSectionId = val),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: DropdownButtonFormField<int>(
                        value: manualPeriod,
                        decoration: const InputDecoration(labelText: 'Period', border: OutlineInputBorder()),
                        items: List.generate(8, (i) => i + 1).map<DropdownMenuItem<int>>((p) {
                          return DropdownMenuItem<int>(
                            value: p,
                            child: Text('Period $p'),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => manualPeriod = val);
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.edit_note),
                    label: const Text('Take Manual Attendance'),
                    onPressed: _navigateToManualAttendance,
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      side: const BorderSide(color: Color(0xFF2563EB)),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildClassCard(Map<String, dynamic> cls, bool isToday) {
    final bool isLive = cls['is_live'] == true;
    final String status = cls['status'] ?? 'Upcoming';
    
    // Styling based on status
    Color borderColor = const Color(0xFF334155);
    Color bgColor = const Color(0xFF1E293B);
    
    if (isLive) {
      borderColor = Colors.blue.withOpacity(0.5);
      bgColor = Colors.blue.withOpacity(0.1);
    } else if (status == 'Completed') {
      bgColor = Colors.grey.withOpacity(0.05);
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
        boxShadow: isLive ? [
          BoxShadow(
            color: Colors.blue.withOpacity(0.2),
            blurRadius: 8,
            offset: const Offset(0, 4),
          )
        ] : null,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () => _navigateToAttendance(cls),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.schedule, size: 16, color: isLive ? Colors.blue : Colors.grey),
                        const SizedBox(width: 6),
                        Text(cls['time'], style: TextStyle(color: isLive ? Colors.blue : Colors.grey, fontWeight: FontWeight.w600)),
                      ],
                    ),
                    if (isLive)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.redAccent.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: Colors.redAccent.withOpacity(0.5)),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.fiber_manual_record, color: Colors.redAccent, size: 10),
                            SizedBox(width: 4),
                            Text('LIVE NOW', style: TextStyle(color: Colors.redAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      )
                    else if (isToday)
                      Text(status, style: TextStyle(color: status == 'Completed' ? Colors.green : Colors.grey, fontSize: 12, fontWeight: FontWeight.bold)),
                  ],
                ),
                const SizedBox(height: 12),
                Text(cls['subject_name'] ?? 'Subject', style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text('${cls['department_name']} • ${cls['year_name']}', style: TextStyle(color: Colors.grey[400], fontSize: 13)),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.05),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text('Period ${cls['period_number']} • Section ${cls['section_name']}', style: const TextStyle(color: Colors.white70, fontSize: 13)),
                    ),
                    if (isLive)
                      const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.blue)
                    else
                      const Icon(Icons.arrow_forward_ios, size: 14, color: Colors.grey),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
