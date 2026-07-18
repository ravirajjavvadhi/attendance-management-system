import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';

class FacultyDashboardScreen extends ConsumerStatefulWidget {
  const FacultyDashboardScreen({super.key});

  @override
  ConsumerState<FacultyDashboardScreen> createState() => _FacultyDashboardScreenState();
}

class _FacultyDashboardScreenState extends ConsumerState<FacultyDashboardScreen> {
  Map<String, dynamic>? activeClass;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchActiveClass();
  }

  Future<void> _fetchActiveClass() async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      // Triggers SchedulingEngine & TimetableEngine natively
      final response = await dio.get('/faculty/timetable/active');
      
      if (mounted) {
        setState(() {
          activeClass = response.data['data']; // Returns Subject, Section, Period
          isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => isLoading = false);
    }
  }

  Future<void> _startAttendance() async {
    if (activeClass == null) return;
    
    try {
      final dio = ref.read(dioClientProvider).dio;
      // Triggers AttendanceEngine.start_attendance_session
      final response = await dio.post('/faculty/attendance/start');
      
      final sessionId = response.data['session_id'];
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Session Started: $sessionId. Opening Scanner...'), backgroundColor: Colors.green),
        );
        // context.pushNamed('attendance_scanner', pathParameters: {'sessionId': sessionId});
      }
    } catch (e) {
       if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to start session: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('EduFlow Command Center'),
        actions: [
          IconButton(icon: const Icon(Icons.calendar_month), onPressed: () {}),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Good Morning, Dr. Kumar', style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 24),
            
            // The flagship one-tap UI
            if (activeClass != null) ...[
              Card(
                color: Colors.blue.shade50,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    children: [
                      const Text('CURRENT LIVE CLASS', style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                      const SizedBox(height: 16),
                      Text(activeClass!['subject_name'], style: Theme.of(context).textTheme.headlineMedium),
                      const SizedBox(height: 8),
                      Text('${activeClass!['branch']} - Section ${activeClass!['section']} (${activeClass!['period_name']})', style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        icon: const Icon(Icons.qr_code_scanner),
                        label: const Text('START ATTENDANCE NOW'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                          backgroundColor: Colors.blue,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
                        ),
                        onPressed: _startAttendance,
                      ),
                    ],
                  ),
                ),
              ),
            ] else ...[
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(32.0),
                  child: Center(child: Text('No active class right now. Enjoy your break!')),
                ),
              ),
            ],
            
            const SizedBox(height: 32),
            Text('Today\'s Schedule', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 16),
            // Mock Timeline
            ListTile(leading: const Icon(Icons.schedule), title: const Text('10:30 AM - Computer Networks'), subtitle: const Text('CSE-A'), trailing: const Icon(Icons.check_circle, color: Colors.green)),
            ListTile(leading: const Icon(Icons.schedule, color: Colors.blue), title: const Text('11:20 AM - Database Systems'), subtitle: const Text('IT-B'), trailing: const Text('LIVE', style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold))),
            ListTile(leading: const Icon(Icons.schedule, color: Colors.grey), title: const Text('2:00 PM - OS Lab'), subtitle: const Text('CSE-A')),
            
          ],
        ),
      ),
      bottomNavigationBar: ModernBottomNav(
        selectedIndex: 0,
        onItemSelected: (index) {},
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.assignment), label: 'Assignments'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
