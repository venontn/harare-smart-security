import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const HsusmsCitizenApp());
}

class HsusmsCitizenApp extends StatelessWidget {
  const HsusmsCitizenApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HSUSMS Citizen',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF3B82F6), brightness: Brightness.dark),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
