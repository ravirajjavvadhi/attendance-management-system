import 'dart:math' as math;

import 'package:dio/dio.dart';
import 'package:eduflow_core/eduflow_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app_router.dart';
import '../../auth/session.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen>
    with SingleTickerProviderStateMixin {
  final _identifierController = TextEditingController();
  late final AnimationController _motionController;
  EduFlowRole _selectedRole = EduFlowRole.parent;
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _motionController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 12),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _identifierController.dispose();
    _motionController.dispose();
    super.dispose();
  }

  String get _label =>
      _selectedRole == EduFlowRole.student ? 'Roll number' : 'Email address';
  String get _hint => _selectedRole == EduFlowRole.student
      ? 'Example: 24AG1A05L6'
      : _selectedRole == EduFlowRole.parent
          ? 'Your registered parent email'
          : 'Your authorised institution email';

  Future<void> _login() async {
    final identifier = _identifierController.text.trim();
    if (identifier.isEmpty) {
      setState(() => _error = 'Enter your $_label.toLowerCase() to continue.');
      return;
    }
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final response = await ref.read(dioClientProvider).dio.post(
        '/auth/passwordless',
        data: {'email': identifier, 'expected_role': _selectedRole.name.toUpperCase()},
      );
      final token = response.data['access_token']?.toString();
      if (token == null) {
        throw const FormatException('No access token was returned.');
      }
      await saveSession(ref, token);
      final actualRole = ref.read(sessionProvider)?.role ?? EduFlowRole.unknown;
      if (!mounted) {
        return;
      }
      context.go(routeForRole(actualRole));
    } on DioException catch (error) {
      final detail = error.response?.data is Map
          ? (error.response?.data['detail']?.toString())
          : null;
      if (mounted) {
        setState(() => _error =
            detail ?? 'Unable to sign in. Check the details and try again.');
      }
    } on FormatException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } catch (_) {
      if (mounted) {
        setState(
            () => _error = 'Unable to sign in right now. Please try again.');
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: AnimatedBuilder(
        animation: _motionController,
        builder: (_, __) => Stack(
          children: [
            _PrismBackground(progress: _motionController.value),
            SafeArea(
              child: Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 460),
                    child: Card(
                      color: theme.colorScheme.surface.withValues(alpha: 0.88),
                      child: Padding(
                        padding: const EdgeInsets.all(28),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Row(children: [
                              Container(
                                width: 44,
                                height: 44,
                                decoration: BoxDecoration(
                                  gradient: const LinearGradient(colors: [
                                    Color(0xFF6D5DFB),
                                    Color(0xFF20D6C2)
                                  ]),
                                  borderRadius: BorderRadius.circular(14),
                                ),
                                child: const Icon(Icons.auto_awesome_rounded,
                                    color: Colors.white),
                              ),
                              const SizedBox(width: 12),
                              Text('KevRyn One',
                                  style: theme.textTheme.titleLarge
                                      ?.copyWith(fontWeight: FontWeight.w800)),
                            ]),
                            const SizedBox(height: 34),
                            Text('Every campus.\nOne intelligent flow.',
                                style: theme.textTheme.displaySmall?.copyWith(
                                    fontWeight: FontWeight.w800, height: 0.96)),
                            const SizedBox(height: 10),
                            Text(
                                'Advanced academic operations, in one flow.',
                                style: theme.textTheme.bodyMedium?.copyWith(
                                    color: theme.colorScheme.onSurfaceVariant)),
                            const SizedBox(height: 26),
                            _RolePicker(
                                selectedRole: _selectedRole,
                                onSelected: (role) => setState(() {
                                      _selectedRole = role;
                                      _error = null;
                                    })),
                            const SizedBox(height: 22),
                            Text(_label,
                                style: theme.textTheme.labelLarge
                                    ?.copyWith(fontWeight: FontWeight.w700)),
                            const SizedBox(height: 8),
                            TextField(
                              controller: _identifierController,
                              keyboardType: _selectedRole == EduFlowRole.student
                                  ? TextInputType.text
                                  : TextInputType.emailAddress,
                              textCapitalization:
                                  _selectedRole == EduFlowRole.student
                                      ? TextCapitalization.characters
                                      : TextCapitalization.none,
                              onSubmitted: (_) => _login(),
                              decoration: InputDecoration(
                                hintText: _hint,
                                prefixIcon: Icon(
                                    _selectedRole == EduFlowRole.student
                                        ? Icons.badge_outlined
                                        : Icons.alternate_email_rounded),
                                border: const OutlineInputBorder(),
                              ),
                            ),
                            if (_error != null) ...[
                              const SizedBox(height: 12),
                              Text(_error!,
                                  style: TextStyle(
                                      color: theme.colorScheme.error)),
                            ],
                            const SizedBox(height: 18),
                            FilledButton.icon(
                              onPressed: _isLoading ? null : _login,
                              icon: _isLoading
                                  ? const SizedBox(
                                      width: 18,
                                      height: 18,
                                      child: CircularProgressIndicator(
                                          strokeWidth: 2))
                                  : const Icon(Icons.arrow_forward_rounded),
                              label: Text(_isLoading
                                  ? 'Opening your workspace…'
                                  : 'Continue securely'),
                              style: FilledButton.styleFrom(
                                  minimumSize: const Size.fromHeight(54)),
                            ),
                            const SizedBox(height: 16),
                            Text(
                                'Your verified account chooses the final workspace.',
                                textAlign: TextAlign.center,
                                style: theme.textTheme.bodySmall?.copyWith(
                                    color: theme.colorScheme.onSurfaceVariant)),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RolePicker extends StatelessWidget {
  const _RolePicker({required this.selectedRole, required this.onSelected});
  final EduFlowRole selectedRole;
  final ValueChanged<EduFlowRole> onSelected;

  @override
  Widget build(BuildContext context) {
    const roles = [
      (EduFlowRole.student, 'Student', Icons.school_outlined),
      (EduFlowRole.faculty, 'Faculty', Icons.co_present_outlined),
      (EduFlowRole.parent, 'Parent', Icons.family_restroom_outlined),
      (
        EduFlowRole.management,
        'Management',
        Icons.dashboard_customize_outlined
      ),
    ];
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: roles
          .map((item) => ChoiceChip(
                selected: selectedRole == item.$1,
                onSelected: (_) => onSelected(item.$1),
                avatar: Icon(item.$3, size: 18),
                label: Text(item.$2),
              ))
          .toList(),
    );
  }
}

class _PrismBackground extends StatelessWidget {
  const _PrismBackground({required this.progress});
  final double progress;

  @override
  Widget build(BuildContext context) {
    final t = Curves.easeInOut.transform(progress);
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
            colors: [Color(0xFF090B18), Color(0xFF151B38)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight),
      ),
      child: Stack(children: [
        Positioned(
            right: -80 + t * 36,
            top: 28 + t * 30,
            child: _Orb(color: const Color(0xFF6D5DFB), size: 260, angle: t)),
        Positioned(
            left: -100 - t * 22,
            bottom: -100 + t * 35,
            child: _Orb(color: const Color(0xFF20D6C2), size: 300, angle: -t)),
      ]),
    );
  }
}

class _Orb extends StatelessWidget {
  const _Orb({required this.color, required this.size, required this.angle});
  final Color color;
  final double size;
  final double angle;

  @override
  Widget build(BuildContext context) => Transform(
        alignment: Alignment.center,
        transform: Matrix4.identity()
          ..setEntry(3, 2, 0.002)
          ..rotateX(angle * .55)
          ..rotateY(angle * math.pi),
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(colors: [
                color.withValues(alpha: .7),
                color.withValues(alpha: 0)
              ])),
        ),
      );
}
