import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:dio/dio.dart';

class FacultyDashboardScreen extends ConsumerStatefulWidget {
  const FacultyDashboardScreen({super.key});

  @override
  ConsumerState<FacultyDashboardScreen> createState() => _FacultyDashboardScreenState();
}

class _FacultyDashboardScreenState extends ConsumerState<FacultyDashboardScreen> {
  List<dynamic> sections = [];
  String? selectedSectionId;
  int selectedPeriod = 1;
  List<dynamic> students = [];
  bool isLoading = true;
  bool isSubmitting = false;
  
  // Live Class info
  bool isLiveClassActive = false;
  String? liveDepartmentName;
  String? liveYearName;
  String? liveSectionName;

  @override
  void initState() {
    super.initState();
    _fetchInitialData();
  }

  Future<void> _fetchInitialData() async {
    try {
      final dio = ref.read(dioClientProvider).dio;
      final response = await dio.get('/academic/sections');
      final List<dynamic> data = response.data;
      
      bool defaultSectionSet = false;
      String? targetSectionId;
      int targetPeriod = 1;
      
      try {
        final liveRes = await dio.get('/academic/faculty/live-class');
        if (liveRes.data != null && liveRes.data['live'] == true) {
          targetSectionId = liveRes.data['section_id'].toString();
          targetPeriod = liveRes.data['period_number'];
          defaultSectionSet = true;
          
          if (mounted) {
            setState(() {
              isLiveClassActive = true;
              liveDepartmentName = liveRes.data['department_name'];
              liveYearName = liveRes.data['year_name'];
              liveSectionName = liveRes.data['section_name'];
            });
          }
        } else {
          if (mounted) setState(() => isLiveClassActive = false);
        }
      } catch (e) {
        debugPrint('Could not fetch live class: $e');
        if (mounted) setState(() => isLiveClassActive = false);
      }
      
      if (mounted) {
        setState(() {
          sections = data;
          if (defaultSectionSet) {
            selectedSectionId = targetSectionId;
            selectedPeriod = targetPeriod;
          } else if (data.isNotEmpty) {
            selectedSectionId = data[0]['id'].toString();
          }
        });
        if (selectedSectionId != null) {
          await _fetchStudents();
        } else {
          setState(() => isLoading = false);
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load sections: $e')),
        );
      }
    }
  }

  Future<void> _fetchStudents() async {
    if (selectedSectionId == null) return;
    setState(() => isLoading = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final response = await dio.get('/academic/students?section_id=$selectedSectionId');
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
    if (selectedSectionId == null || students.isEmpty) return;
    setState(() => isSubmitting = true);
    try {
      final dio = ref.read(dioClientProvider).dio;
      final todayStr = DateTime.now().toIso8601String().split('T')[0];
      
      final records = students.map((s) => {
        'student_id': s['id'],
        'is_present': s['present'],
      }).toList();

      await dio.post('/attendance/submit', data: {
        'section_id': int.parse(selectedSectionId!),
        'date': todayStr,
        'period': selectedPeriod,
        'records': records,
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Attendance submitted successfully!'), backgroundColor: Colors.green),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to submit attendance: $e'), backgroundColor: Colors.red),
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
        title: const Text('Faculty Command Center'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _fetchInitialData,
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (isLiveClassActive)
              Container(
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, color: Colors.blue),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Live Class Auto-Selected:', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue)),
                          Text('$liveDepartmentName • $liveYearName • Sec $liveSectionName (Period $selectedPeriod)', style: const TextStyle(color: Colors.blueGrey)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            // Dropdowns for Section and Period selection
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: selectedSectionId,
                    decoration: const InputDecoration(labelText: 'Select Section', border: OutlineInputBorder()),
                    items: sections.map<DropdownMenuItem<String>>((s) {
                      return DropdownMenuItem<String>(
                        value: s['id'].toString(),
                        child: Text(s['name'] ?? 'Section'),
                      );
                    }).toList(),
                    onChanged: (val) {
                      setState(() {
                        selectedSectionId = val;
                      });
                      _fetchStudents();
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: DropdownButtonFormField<int>(
                    value: selectedPeriod,
                    decoration: const InputDecoration(labelText: 'Select Period', border: OutlineInputBorder()),
                    items: List.generate(8, (i) => i + 1).map<DropdownMenuItem<int>>((p) {
                      return DropdownMenuItem<int>(
                        value: p,
                        child: Text('Period $p'),
                      );
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) {
                        setState(() {
                          selectedPeriod = val;
                        });
                      }
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            
            // Student list
            Expanded(
              child: isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : students.isEmpty
                      ? const Center(child: Text('No students found in this section.'))
                      : ListView.builder(
                          itemCount: students.length,
                          itemBuilder: (context, index) {
                            final student = students[index];
                            final isPresent = student['present'] as bool;
                            return Card(
                              margin: const EdgeInsets.only(bottom: 8),
                              child: ListTile(
                                leading: CircleAvatar(
                                  backgroundColor: isPresent ? Colors.green.shade100 : Colors.red.shade100,
                                  child: Text(
                                    student['name']?.substring(0, 1) ?? 'S',
                                    style: TextStyle(color: isPresent ? Colors.green.shade800 : Colors.red.shade800),
                                  ),
                                ),
                                title: Text(student['name'] ?? 'Student'),
                                subtitle: Text('Roll: ${student['roll_number'] ?? '-'}'),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    ChoiceChip(
                                      label: const Text('P'),
                                      selected: isPresent,
                                      selectedColor: Colors.green.shade200,
                                      onSelected: (val) {
                                        setState(() {
                                          students[index]['present'] = true;
                                        });
                                      },
                                    ),
                                    const SizedBox(width: 8),
                                    ChoiceChip(
                                      label: const Text('A'),
                                      selected: !isPresent,
                                      selectedColor: Colors.red.shade200,
                                      onSelected: (val) {
                                        setState(() {
                                          students[index]['present'] = false;
                                        });
                                      },
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
            ),
            
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: isSubmitting || students.isEmpty ? null : _submitAttendance,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              child: isSubmitting
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text('SUBMIT ATTENDANCE', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }
}
