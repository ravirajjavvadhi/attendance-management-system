import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:go_router/go_router.dart';
import 'package:dio/dio.dart';

class AttendanceTrackingScreen extends ConsumerStatefulWidget {
  final String sectionId;
  final int periodNumber;
  final String subjectName;
  final String classDetails;
  final String timeStr;

  const AttendanceTrackingScreen({
    super.key,
    required this.sectionId,
    required this.periodNumber,
    required this.subjectName,
    required this.classDetails,
    required this.timeStr,
  });

  @override
  ConsumerState<AttendanceTrackingScreen> createState() => _AttendanceTrackingScreenState();
}

class _AttendanceTrackingScreenState extends ConsumerState<AttendanceTrackingScreen> {
  List<dynamic> students = [];
  bool isLoading = true;
  bool isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _fetchStudents();
  }

  Future<void> _fetchStudents() async {
    setState(() => isLoading = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final response = await dio.get('/academic/students?section_id=${widget.sectionId}');
      final List<dynamic> data = response.data;
      if (mounted) {
        setState(() {
          students = data.map((s) {
            return {
              'id': s['id'],
              'roll_number': s['roll_number'],
              'name': s['name'] == 'Not Provided' ? 'Student' : s['name'],
              'present': true, // Default to present
            };
          }).toList();
          isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load students: $e')),
        );
      }
    }
  }

  Future<void> _submitAttendance() async {
    if (students.isEmpty) return;
    setState(() => isSubmitting = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final todayStr = DateTime.now().toIso8601String().split('T')[0];
      
      final records = students.map((s) => {
        'student_id': s['id'],
        'is_present': s['present'],
      }).toList();

      await dio.post('/attendance/submit', data: {
        'section_id': int.parse(widget.sectionId),
        'date': todayStr,
        'period': widget.periodNumber,
        'records': records,
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Attendance submitted successfully!'), backgroundColor: Colors.green),
        );
        context.pop(); // Go back to schedule
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to submit attendance: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Track Attendance'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: Column(
        children: [
          // Class Header
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              border: const Border(bottom: BorderSide(color: Color(0xFF334155))),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.class_, color: Colors.blue, size: 32),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(widget.subjectName, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
                      const SizedBox(height: 4),
                      Text(widget.classDetails, style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 14)),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          Icon(Icons.schedule, size: 14, color: Colors.white.withOpacity(0.5)),
                          const SizedBox(width: 6),
                          Text('Period ${widget.periodNumber} • ${widget.timeStr}', style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 13)),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // Student List
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator())
                : students.isEmpty
                    ? const Center(child: Text('No students found in this section.'))
                    : ListView.builder(
                        itemCount: students.length,
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        itemBuilder: (context, index) {
                          final student = students[index];
                          final isPresent = student['present'] as bool;
                          
                          return Container(
                            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                            decoration: BoxDecoration(
                              color: const Color(0xFF1E293B),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: const Color(0xFF334155)),
                            ),
                            child: ListTile(
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                              leading: CircleAvatar(
                                backgroundColor: isPresent ? Colors.green.withOpacity(0.2) : Colors.red.withOpacity(0.2),
                                child: Text(
                                  student['name'][0].toUpperCase(),
                                  style: TextStyle(
                                    color: isPresent ? Colors.green : Colors.red,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                              title: Text(student['name'], style: const TextStyle(fontWeight: FontWeight.w600)),
                              subtitle: Text('Roll: ${student['roll_number']}'),
                              trailing: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  // Present Button
                                  InkWell(
                                    onTap: () {
                                      setState(() {
                                        students[index]['present'] = true;
                                      });
                                    },
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                      decoration: BoxDecoration(
                                        color: isPresent ? Colors.green.withOpacity(0.2) : Colors.transparent,
                                        borderRadius: const BorderRadius.horizontal(left: Radius.circular(8)),
                                        border: Border.all(color: isPresent ? Colors.green : Colors.grey.withOpacity(0.3)),
                                      ),
                                      child: Row(
                                        children: [
                                          if (isPresent) const Icon(Icons.check, size: 16, color: Colors.green),
                                          if (isPresent) const SizedBox(width: 4),
                                          Text('P', style: TextStyle(color: isPresent ? Colors.green : Colors.grey, fontWeight: FontWeight.bold)),
                                        ],
                                      ),
                                    ),
                                  ),
                                  // Absent Button
                                  InkWell(
                                    onTap: () {
                                      setState(() {
                                        students[index]['present'] = false;
                                      });
                                    },
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                      decoration: BoxDecoration(
                                        color: !isPresent ? Colors.red.withOpacity(0.2) : Colors.transparent,
                                        borderRadius: const BorderRadius.horizontal(right: Radius.circular(8)),
                                        border: Border.all(color: !isPresent ? Colors.red : Colors.grey.withOpacity(0.3)),
                                      ),
                                      child: Text('A', style: TextStyle(color: !isPresent ? Colors.red : Colors.grey, fontWeight: FontWeight.bold)),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
          
          // Submit Button
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: isSubmitting || students.isEmpty ? null : _submitAttendance,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: isSubmitting
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Text('SUBMIT ATTENDANCE', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 1)),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
