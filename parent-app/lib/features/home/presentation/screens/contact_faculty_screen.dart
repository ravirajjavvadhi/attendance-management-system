import 'package:flutter/material.dart';

class ContactFacultyScreen extends StatelessWidget {
  const ContactFacultyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Contact Faculty'), centerTitle: true),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          _FacultyCard(subject: 'Mathematics', name: 'Dr. Smith', email: 'smith@eduflow.edu', phone: '+1 555-0101'),
          _FacultyCard(subject: 'Physics', name: 'Prof. Johnson', email: 'johnson@eduflow.edu', phone: '+1 555-0102'),
          _FacultyCard(subject: 'Chemistry', name: 'Dr. Kumar', email: 'kumar@eduflow.edu', phone: '+1 555-0103'),
        ],
      ),
    );
  }
}

class _FacultyCard extends StatelessWidget {
  final String subject;
  final String name;
  final String email;
  final String phone;

  const _FacultyCard({required this.subject, required this.name, required this.email, required this.phone});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(subject, style: const TextStyle(fontSize: 14, color: Colors.grey, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(name, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: OutlinedButton.icon(onPressed: () {}, icon: const Icon(Icons.email), label: const Text('Email'))),
                const SizedBox(width: 12),
                Expanded(child: ElevatedButton.icon(onPressed: () {}, icon: const Icon(Icons.call), label: const Text('Call'))),
              ],
            )
          ],
        ),
      ),
    );
  }
}
