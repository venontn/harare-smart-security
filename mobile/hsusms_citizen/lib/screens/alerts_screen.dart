import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> {
  List<dynamic> alerts = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => loading = true);
    try {
      alerts = await ApiService.listAlerts();
    } catch (_) {
      alerts = [];
    }
    setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Public Alerts'), backgroundColor: const Color(0xFF0F1A30)),
      backgroundColor: const Color(0xFF0B1220),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: alerts.isEmpty
                  ? const Center(child: Text('No active alerts', style: TextStyle(color: Colors.white54)))
                  : ListView.builder(
                      itemCount: alerts.length,
                      itemBuilder: (_, i) {
                        final a = alerts[i] as Map<String, dynamic>;
                        return Card(
                          color: const Color(0xFF141E33),
                          margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          child: ListTile(
                            title: Text(a['message'] ?? '', style: const TextStyle(color: Colors.white)),
                            subtitle: Text('${a['zone']} · ${a['severity']}', style: const TextStyle(color: Colors.white54)),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
