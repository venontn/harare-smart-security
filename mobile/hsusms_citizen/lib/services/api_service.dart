import 'dart:convert';
import 'package:http/http.dart' as http;

/// Default API base — change for device/emulator:
/// - Android emulator: http://10.0.2.2:8000
/// - iOS simulator: http://127.0.0.1:8000
/// - Physical device: http://<your-pc-ip>:8000
class ApiService {
  static String baseUrl = 'http://127.0.0.1:8000/api';

  static Future<Map<String, dynamic>> health() async {
    final res = await http.get(Uri.parse('$baseUrl/health'));
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> dashboardStats() async {
    final res = await http.get(Uri.parse('$baseUrl/dashboard/stats'));
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  static Future<List<dynamic>> listAlerts() async {
    final res = await http.get(Uri.parse('$baseUrl/alerts?acknowledged=false'));
    return jsonDecode(res.body) as List<dynamic>;
  }

  static Future<Map<String, dynamic>> submitReport({
    required String reportType,
    required String description,
    required double latitude,
    required double longitude,
    String reporterName = 'Anonymous',
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/citizen/reports'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'reporter_name': reporterName,
        'report_type': reportType,
        'description': description,
        'latitude': latitude,
        'longitude': longitude,
      }),
    );
    if (res.statusCode >= 400) {
      throw Exception(res.body);
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> submitEmergency({
    required String description,
    required double latitude,
    required double longitude,
    String reporterName = 'Citizen',
  }) async {
    return submitReport(
      reportType: 'emergency',
      description: description,
      latitude: latitude,
      longitude: longitude,
      reporterName: reporterName,
    );
  }
}
