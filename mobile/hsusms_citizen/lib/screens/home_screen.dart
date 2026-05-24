import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'alerts_screen.dart';
import 'emergency_screen.dart';
import 'report_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? stats;
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      await ApiService.health();
      final s = await ApiService.dashboardStats();
      setState(() {
        stats = s;
        loading = false;
      });
    } catch (e) {
      setState(() {
        error = 'Cannot reach HSUSMS server.\nSet ApiService.baseUrl in api_service.dart\n\n$e';
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('HSUSMS Citizen'),
        backgroundColor: const Color(0xFF0F1A30),
        foregroundColor: Colors.white,
      ),
      backgroundColor: const Color(0xFF0B1220),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
              color: const Color(0xFF141E33),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Harare Smart Urban Security',
                      style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      loading ? 'Connecting...' : error ?? 'System online',
                      style: TextStyle(color: error != null ? Colors.redAccent : Colors.greenAccent),
                    ),
                  ],
                ),
              ),
            ),
            if (stats != null) ...[
              const SizedBox(height: 12),
              _statRow('Active Incidents', stats!['active_incidents']),
              _statRow('Open Alerts', stats!['open_alerts']),
              _statRow('Cameras Online', stats!['cameras_online']),
            ],
            const SizedBox(height: 20),
            _actionCard(
              context,
              icon: Icons.warning_amber,
              color: Colors.red,
              title: 'Emergency Panic',
              subtitle: 'Instant high-priority alert to command center',
              onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const EmergencyScreen())),
            ),
            _actionCard(
              context,
              icon: Icons.report,
              color: Colors.blue,
              title: 'Report Incident',
              subtitle: 'Crime, theft, traffic, vandalism',
              onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ReportScreen())),
            ),
            _actionCard(
              context,
              icon: Icons.notifications,
              color: Colors.orange,
              title: 'Public Alerts',
              subtitle: 'View active city safety alerts',
              onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AlertsScreen())),
            ),
          ],
        ),
      ),
    );
  }

  Widget _statRow(String label, dynamic value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.white70)),
          Text('$value', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _actionCard(
    BuildContext context, {
    required IconData icon,
    required Color color,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Card(
      color: const Color(0xFF141E33),
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(backgroundColor: color.withOpacity(0.2), child: Icon(icon, color: color)),
        title: Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
        subtitle: Text(subtitle, style: const TextStyle(color: Colors.white54)),
        trailing: const Icon(Icons.chevron_right, color: Colors.white54),
        onTap: onTap,
      ),
    );
  }
}
