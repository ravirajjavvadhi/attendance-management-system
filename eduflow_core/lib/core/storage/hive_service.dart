import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class HiveService {
  static Future<void> init() async {
    await Hive.initFlutter();
    await Hive.openBox('parent_dashboard');
    await Hive.openBox('settings');
  }

  Box getBox(String boxName) {
    return Hive.box(boxName);
  }
  
  Future<void> cacheDashboardData(Map<String, dynamic> data) async {
    final box = getBox('parent_dashboard');
    await box.put('latest_data', data);
  }
  
  Map<String, dynamic>? getCachedDashboardData() {
    final box = getBox('parent_dashboard');
    final data = box.get('latest_data');
    if (data != null) {
      return Map<String, dynamic>.from(data);
    }
    return null;
  }
}

final hiveServiceProvider = Provider<HiveService>((ref) {
  return HiveService();
});
