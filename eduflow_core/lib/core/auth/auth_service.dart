import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  final SharedPreferences _prefs;

  AuthService(this._prefs);

  Future<void> saveToken(String token) async {
    await _prefs.setString('jwt_token', token);
  }

  String? getToken() {
    return _prefs.getString('jwt_token');
  }

  Future<void> clearSession() async {
    await _prefs.remove('jwt_token');
    // Also clear Biometrics flag and PIN if needed
  }

  Future<bool> verifyBiometrics() async {
    // Uses local_auth to verify fingerprint/face id
    // Mocking true for the architecture skeleton
    return true;
  }
}

final authServiceProvider = Provider<AuthService>((ref) {
  throw UnimplementedError('authServiceProvider not initialized');
});
