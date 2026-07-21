import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../main.dart';

final parentProfileProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final dioClient = ref.watch(dioClientProvider);
  try {
    final response = await dioClient.dio.get('/parent/profile');
    return response.data['data'];
  } catch (e) {
    return {
      'name': 'Parent',
      'email': 'N/A',
      'mobile': null,
      'relationship': null,
      'students': [],
    };
  }
});

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(parentProfileProvider);
    final themeMode = ref.watch(themeModeProvider);
    final isDark = themeMode == ThemeMode.dark || 
                   (themeMode == ThemeMode.system && Theme.of(context).brightness == Brightness.dark);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/home'),
        ),
      ),
      body: profileAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Error loading profile: $err')),
        data: (profile) {
          final students = (profile['students'] as List?) ?? [];

          return SingleChildScrollView(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // ── Profile Header ──
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: isDark
                          ? [const Color(0xFF1E293B), const Color(0xFF334155)]
                          : [const Color(0xFF6366F1), const Color(0xFF8B5CF6)],
                    ),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 40,
                        backgroundColor: Colors.white.withOpacity(0.2),
                        child: Text(
                          (profile['name'] ?? 'P').toString().isNotEmpty
                              ? (profile['name'] ?? 'P').toString()[0].toUpperCase()
                              : 'P',
                          style: const TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        profile['name'] ?? 'Parent',
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        profile['email'] ?? '',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white.withOpacity(0.8),
                        ),
                      ),
                      if (profile['relationship'] != null) ...[
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.15),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            profile['relationship'],
                            style: const TextStyle(color: Colors.white, fontSize: 12),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // ── Contact Info ──
                _buildSectionTitle(context, 'Contact Information'),
                const SizedBox(height: 8),
                _buildInfoTile(context, Icons.email, 'Email', profile['email'] ?? 'Not set'),
                _buildInfoTile(context, Icons.phone, 'Mobile', profile['mobile'] ?? 'Not set'),
                const SizedBox(height: 24),

                // ── Linked Students ──
                _buildSectionTitle(context, 'Linked Students'),
                const SizedBox(height: 8),
                if (students.isEmpty)
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Theme.of(context).cardColor,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey.withOpacity(0.2)),
                    ),
                    child: const Text(
                      'No students linked to your account yet.',
                      style: TextStyle(color: Colors.grey),
                      textAlign: TextAlign.center,
                    ),
                  )
                else
                  ...students.map<Widget>((s) => Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Theme.of(context).cardColor,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.grey.withOpacity(0.1)),
                        ),
                        child: Row(
                          children: [
                            CircleAvatar(
                              radius: 20,
                              backgroundColor: Colors.indigo.withOpacity(0.1),
                              child: const Icon(Icons.person, color: Colors.indigo),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    s['name'] ?? 'Student',
                                    style: const TextStyle(fontWeight: FontWeight.bold),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    '${s['roll_number'] ?? ''} • ${s['department'] ?? ''} • ${s['class'] ?? ''} - ${s['section'] ?? ''}',
                                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      )),
                const SizedBox(height: 24),

                // ── App Preferences ──
                _buildSectionTitle(context, 'Preferences'),
                const SizedBox(height: 8),
                _buildSettingTile(context, Icons.notifications, 'Push Notifications', trailing: Switch(
                  value: true,
                  onChanged: (_) {},
                  activeColor: Colors.indigo,
                )),
                _buildSettingTile(context, Icons.dark_mode, 'Dark Mode', trailing: Switch(
                  value: isDark,
                  onChanged: (val) async {
                    ref.read(themeModeProvider.notifier).state = val ? ThemeMode.dark : ThemeMode.light;
                    final prefs = await SharedPreferences.getInstance();
                    prefs.setBool('isDarkMode', val);
                  },
                  activeColor: Colors.indigo,
                )),
                _buildSettingTile(context, Icons.language, 'Language', subtitle: 'English'),
                const SizedBox(height: 24),

                // ── About ──
                _buildSectionTitle(context, 'About'),
                const SizedBox(height: 8),
                _buildSettingTile(context, Icons.info, 'App Version', subtitle: '1.0.0'),
                _buildSettingTile(context, Icons.policy, 'Privacy Policy'),
                _buildSettingTile(context, Icons.description, 'Terms of Service'),
                const SizedBox(height: 32),

                // ── Sign Out ──
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () async {
                      final confirmed = await showDialog<bool>(
                        context: context,
                        builder: (ctx) => AlertDialog(
                          title: const Text('Sign Out'),
                          content: const Text('Are you sure you want to sign out?'),
                          actions: [
                            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
                            TextButton(
                              onPressed: () => Navigator.pop(ctx, true),
                              child: const Text('Sign Out', style: TextStyle(color: Colors.red)),
                            ),
                          ],
                        ),
                      );
                      if (confirmed == true && context.mounted) {
                        final authService = ref.read(authServiceProvider);
                        await authService.clearSession();
                        if (context.mounted) context.go('/login');
                      }
                    },
                    icon: const Icon(Icons.logout, color: Colors.white),
                    label: const Text('Sign Out', style: TextStyle(color: Colors.white)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                ),
                const SizedBox(height: 32),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildSectionTitle(BuildContext context, String title) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
    );
  }

  Widget _buildInfoTile(BuildContext context, IconData icon, String label, String value) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey),
          const SizedBox(width: 12),
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
          const Spacer(),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildSettingTile(BuildContext context, IconData icon, String title, {String? subtitle, Widget? trailing}) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: EdgeInsets.symmetric(horizontal: 16, vertical: trailing != null ? 4 : 14),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 14)),
                if (subtitle != null)
                  Text(subtitle, style: const TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
          ),
          if (trailing != null) trailing,
        ],
      ),
    );
  }
}
