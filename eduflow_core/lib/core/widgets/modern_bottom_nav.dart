import 'package:flutter/material.dart';

class ModernBottomNav extends StatelessWidget {
  final int selectedIndex;
  final Function(int) onItemSelected;
  final List<NavigationDestination> destinations;

  const ModernBottomNav({
    super.key,
    required this.selectedIndex,
    required this.onItemSelected,
    required this.destinations,
  });

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: selectedIndex,
      onDestinationSelected: onItemSelected,
      destinations: destinations,
    );
  }
}
