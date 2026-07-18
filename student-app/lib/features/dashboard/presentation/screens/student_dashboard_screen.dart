import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';

class StudentDashboardScreen extends ConsumerWidget {
  const StudentDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('EduFlow Student'),
        actions: [
          IconButton(icon: const Icon(Icons.qr_code_scanner), onPressed: () {}), // For digital ID scanning
          IconButton(icon: const Icon(Icons.person), onPressed: () {}),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 1. The Hero Header (Today's Pulse)
            Text('Good Morning, Ankit', style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 24),
            _buildPulseCard(context),
            const SizedBox(height: 24),
            
            // 2. Live Schedule & Attendance
            Row(
              children: [
                Expanded(flex: 3, child: _buildNextClassCard(context)),
                const SizedBox(width: 16),
                Expanded(flex: 2, child: _buildAttendanceRing(context)),
              ],
            ),
            const SizedBox(height: 32),
            
            // 3. The Academic Grid
            Text('My Academics', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              mainAxisSpacing: 16,
              crossAxisSpacing: 16,
              childAspectRatio: 1.5,
              children: [
                _buildGridAction(context, 'Assignments', Icons.assignment, Colors.orange, badge: '2 Pending'),
                _buildGridAction(context, 'Study Material', Icons.menu_book, Colors.blue),
                _buildGridAction(context, 'Timetable', Icons.calendar_view_week, Colors.purple),
                _buildGridAction(context, 'Results', Icons.grade, Colors.green),
              ],
            ),
          ],
        ),
      ),
      bottomNavigationBar: ModernBottomNav(
        selectedIndex: 0,
        onItemSelected: (index) {},
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.chat_bubble), label: 'AI Tutor'),
          NavigationDestination(icon: Icon(Icons.more_horiz), label: 'Menu'),
        ],
      ),
    );
  }

  Widget _buildPulseCard(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.indigo.shade900,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: Colors.indigo.withOpacity(0.3), blurRadius: 10, offset: const Offset(0, 5))],
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('EXAM COUNTDOWN', style: TextStyle(color: Colors.white70, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
              Icon(Icons.timer, color: Colors.indigo.shade200, size: 16),
            ],
          ),
          const SizedBox(height: 12),
          const Text('12 Days until', style: TextStyle(color: Colors.white, fontSize: 16)),
          const Text('Mid-Semester', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          
          // AI Tutor Insight
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: Colors.white.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
            child: Row(
              children: [
                const Icon(Icons.auto_awesome, color: Colors.orangeAccent, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Text('Your OS assignment is due in 14 hours. Want to review the notes?', style: TextStyle(color: Colors.indigo.shade100, fontSize: 13)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNextClassCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('NEXT CLASS', style: TextStyle(color: Colors.grey, fontSize: 10, fontWeight: FontWeight.bold)),
          SizedBox(height: 12),
          Text('10:30 AM', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 4),
          Text('Computer Networks', style: TextStyle(fontSize: 14)),
          SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.meeting_room, size: 12, color: Colors.blue),
              SizedBox(width: 4),
              Text('Room 304', style: TextStyle(fontSize: 12, color: Colors.grey)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAttendanceRing(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 60,
                height: 60,
                child: CircularProgressIndicator(
                  value: 0.82,
                  backgroundColor: Colors.grey.withOpacity(0.2),
                  color: Colors.green,
                  strokeWidth: 6,
                ),
              ),
              const Text('82%', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            ],
          ),
          const SizedBox(height: 12),
          const Text('Attendance', style: TextStyle(fontSize: 12, color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _buildGridAction(BuildContext context, String title, IconData icon, Color color, {String? badge}) {
    return Container(
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(icon, color: color, size: 28),
                const Spacer(),
                Text(title, style: TextStyle(fontWeight: FontWeight.bold, color: color.withOpacity(0.8))),
              ],
            ),
          ),
          if (badge != null)
            Positioned(
              top: 12,
              right: 12,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(color: Colors.redAccent, borderRadius: BorderRadius.circular(8)),
                child: Text(badge, style: const TextStyle(color: Colors.white, fontSize: 8, fontWeight: FontWeight.bold)),
              ),
            ),
        ],
      ),
    );
  }
}
