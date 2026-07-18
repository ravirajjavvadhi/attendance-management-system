import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:eduflow_core/eduflow_core.dart';

class OtpScreen extends ConsumerWidget {
  final String mobileNumber;

  const OtpScreen({super.key, required this.mobileNumber});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final otpController = TextEditingController();
    final instCodeController = TextEditingController();
    final rollNoController = TextEditingController();
    final dobController = TextEditingController(); // Assuming string for mock

    return Scaffold(
      appBar: AppBar(title: const Text('Verify Account')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Enter the OTP sent to $mobileNumber'),
            const SizedBox(height: 16),
            TextFormField(
              controller: otpController,
              decoration: const InputDecoration(labelText: '6-Digit OTP', border: OutlineInputBorder()),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 32),
            const Text('Link Student Details', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            const SizedBox(height: 16),
            TextFormField(
              controller: instCodeController,
              decoration: const InputDecoration(labelText: 'Institution Code', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: rollNoController,
              decoration: const InputDecoration(labelText: 'Roll Number', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: dobController,
              decoration: const InputDecoration(labelText: 'Date of Birth (YYYY-MM-DD)', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 32),
            FilledButton(
              onPressed: () async {
                try {
                  final dio = ref.read(dioClientProvider).dio;
                  final authService = ref.read(authServiceProvider);

                  // 1. Verify OTP
                  final otpRes = await dio.post('/parent/auth/verify-otp', data: {
                    'mobile_number': mobileNumber,
                    'otp': otpController.text,
                  });
                  
                  final token = otpRes.data['access_token'];
                  await authService.saveToken(token); // Save token securely

                  // 2. Link Student (now authenticated with token due to interceptor)
                  await dio.post('/parent/auth/link-student', data: {
                    'institution_code': instCodeController.text,
                    'roll_number': rollNoController.text,
                    'dob': dobController.text,
                    'relationship': 'PRIMARY',
                  });

                  // Success, go home
                  if (context.mounted) {
                    context.go('/home');
                  }
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Verification Failed: $e')));
                  }
                }
              },
              child: const Text('Verify & Link Student'),
            ),
          ],
        ),
      ),
    );
  }
}
