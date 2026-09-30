import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app_router.dart';
import '../../auth/session.dart';

class KevRynLaunchScreen extends ConsumerStatefulWidget {
  const KevRynLaunchScreen({super.key});
  @override
  ConsumerState<KevRynLaunchScreen> createState() => _KevRynLaunchScreenState();
}

class _KevRynLaunchScreenState extends ConsumerState<KevRynLaunchScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  @override
  void initState() { super.initState(); _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 1800))..forward(); Future<void>.delayed(const Duration(milliseconds: 2200), _continue); }
  void _continue() { if (!mounted) return; final session = ref.read(sessionProvider); context.go(session == null ? '/login' : routeForRole(session.role)); }
  @override
  void dispose() { _controller.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) => Scaffold(body: AnimatedBuilder(animation: _controller, builder: (_, __) { final t = Curves.easeOutCubic.transform(_controller.value); return Stack(children: [const DecoratedBox(decoration: BoxDecoration(gradient: LinearGradient(colors: [Color(0xFF050714), Color(0xFF172353), Color(0xFF080B1D)], begin: Alignment.topLeft, end: Alignment.bottomRight))), Positioned(right: -100 + 50*t, top: -80 + 30*t, child: _Glow(size: 320, color: const Color(0xFF745DFF), angle: t)), Positioned(left: -130, bottom: -110 + 40*t, child: _Glow(size: 350, color: const Color(0xFF22D7C2), angle: -t)), Center(child: Opacity(opacity: t, child: Transform.scale(scale: .82 + .18*t, child: Column(mainAxisSize: MainAxisSize.min, children: [Container(width: 96, height: 96, decoration: BoxDecoration(borderRadius: BorderRadius.circular(30), gradient: const LinearGradient(colors: [Color(0xFF8A72FF), Color(0xFF22D7C2)]), boxShadow: const [BoxShadow(color: Color(0x88745DFF), blurRadius: 42, spreadRadius: 4)]), child: const Icon(Icons.auto_awesome_rounded, color: Colors.white, size: 46)), const SizedBox(height: 26), const Text('KevRyn One', style: TextStyle(color: Colors.white, fontSize: 34, fontWeight: FontWeight.w900, letterSpacing: -.8)), const SizedBox(height: 10), const Text('ADVANCED ACADEMIC OPERATIONS, IN ONE FLOW', style: TextStyle(color: Color(0xFFBFEFFD), fontWeight: FontWeight.w800, fontSize: 11, letterSpacing: 1.45)), const SizedBox(height: 34), SizedBox(width: 112, child: LinearProgressIndicator(value: t, minHeight: 3, borderRadius: BorderRadius.circular(10), color: const Color(0xFF22D7C2), backgroundColor: Colors.white24))]))))]); }));
}
class _Glow extends StatelessWidget { const _Glow({required this.size, required this.color, required this.angle}); final double size; final Color color; final double angle; @override Widget build(BuildContext context) => Transform.rotate(angle: angle * math.pi / 3, child: Container(width: size, height: size, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [color.withValues(alpha: .38), color.withValues(alpha: 0)])))); }
