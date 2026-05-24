import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../services/api_service.dart';

class ReportScreen extends StatefulWidget {
  const ReportScreen({super.key});

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> {
  final _name = TextEditingController();
  final _desc = TextEditingController();
  String _type = 'crime';
  bool sending = false;

  Future<void> _submit() async {
    if (_desc.text.trim().isEmpty) return;
    setState(() => sending = true);
    try {
      Position? pos;
      try {
        pos = await Geolocator.getCurrentPosition();
      } catch (_) {}
      final r = await ApiService.submitReport(
        reportType: _type,
        description: _desc.text.trim(),
        latitude: pos?.latitude ?? -17.8292,
        longitude: pos?.longitude ?? 31.0537,
        reporterName: _name.text.trim().isEmpty ? 'Anonymous' : _name.text.trim(),
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Report submitted #${r['id']}')),
      );
      Navigator.pop(context);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Report Incident'), backgroundColor: const Color(0xFF0F1A30)),
      backgroundColor: const Color(0xFF0B1220),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: _name,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(labelText: 'Your name (optional)', labelStyle: TextStyle(color: Colors.white54)),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: _type,
            dropdownColor: const Color(0xFF141E33),
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(labelText: 'Report type', labelStyle: TextStyle(color: Colors.white54)),
            items: const [
              DropdownMenuItem(value: 'crime', child: Text('Crime')),
              DropdownMenuItem(value: 'theft', child: Text('Theft')),
              DropdownMenuItem(value: 'traffic', child: Text('Traffic')),
              DropdownMenuItem(value: 'vandalism', child: Text('Vandalism')),
              DropdownMenuItem(value: 'emergency', child: Text('Emergency')),
            ],
            onChanged: (v) => setState(() => _type = v ?? 'crime'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _desc,
            maxLines: 5,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(labelText: 'Description', labelStyle: TextStyle(color: Colors.white54)),
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: sending ? null : _submit,
            child: sending ? const CircularProgressIndicator() : const Text('Submit Report'),
          ),
        ],
      ),
    );
  }
}
