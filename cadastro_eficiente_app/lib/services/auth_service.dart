import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static Future<void> salvarUsuario(Map<String, dynamic> user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('user_data', jsonEncode(user));
  }

  static Future<Map<String, dynamic>?> getUsuario() async {
    final prefs = await SharedPreferences.getInstance();
    final data = prefs.getString('user_data');

    if (data != null) {
      return jsonDecode(data);
    }
    return null;
  }

  static Future<bool> loginOffline(String username) async {
    final user = await getUsuario();

    if (user != null && user['username'] == username) {
      return true;
    }

    return false;
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('user_data');
  }
}