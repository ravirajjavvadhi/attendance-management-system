import 'package:flutter/material.dart';

class DocumentsScreen extends StatelessWidget {
  const DocumentsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Documents & Resources'), centerTitle: true),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          const Text('Academic Records', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          _DocumentTile(title: 'Term 1 Report Card', date: 'Jul 15, 2026', type: 'PDF'),
          
          const SizedBox(height: 24),
          const Text('Financial Receipts', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          _DocumentTile(title: 'Semester 1 Fee Receipt', date: 'Jun 01, 2026', type: 'PDF'),
          
          const SizedBox(height: 24),
          const Text('General', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          _DocumentTile(title: 'School Rules & Regulations', date: 'Jan 10, 2026', type: 'DOCX'),
        ],
      ),
    );
  }
}

class _DocumentTile extends StatelessWidget {
  final String title;
  final String date;
  final String type;

  const _DocumentTile({required this.title, required this.date, required this.type});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: Colors.grey.shade300)),
      leading: Icon(
        type == 'PDF' ? Icons.picture_as_pdf : Icons.description,
        color: type == 'PDF' ? Colors.red : Colors.blue,
        size: 32,
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
      subtitle: Text('Issued: $date'),
      trailing: IconButton(
        icon: const Icon(Icons.download, color: Colors.blue),
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Downloading $title...')));
        },
      ),
    );
  }
}
