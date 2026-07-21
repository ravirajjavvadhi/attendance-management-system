import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class HiveService {
  static Future<void> init() async {
    await Hive.initFlutter();
    await Hive.openBox('parent_dashboard');
    await Hive.openBox('notifications');
    await Hive.openBox('settings');
  }

  Box getBox(String boxName) {
    return Hive.box(boxName);
  }
  
  Future<void> cacheDashboardData(Map<String, dynamic> data) async {
    final box = getBox('parent_dashboard');
    await box.put('mega_payload', data);
    
    // Auto-extract and cache notifications separately for easy access
    if (data.containsKey('notifications')) {
      await cacheNotifications(List<Map<String, dynamic>>.from(data['notifications']));
    }
  }
  
  Map<String, dynamic>? getCachedDashboardData() {
    final box = getBox('parent_dashboard');
    final data = box.get('mega_payload');
    if (data != null) {
      return Map<String, dynamic>.from(data);
    }
    return null;
  }

  Future<void> cacheNotifications(List<Map<String, dynamic>> notifications) async {
    final box = getBox('notifications');
    await box.put('all', notifications);
  }

  List<Map<String, dynamic>> getCachedNotifications() {
    final box = getBox('notifications');
    final data = box.get('all');
    if (data != null) {
      return List<Map<String, dynamic>>.from(data.map((e) => Map<String, dynamic>.from(e)));
    }
    return [];
  }
}

final hiveServiceProvider = Provider<HiveService>((ref) {
  return HiveService();
});
