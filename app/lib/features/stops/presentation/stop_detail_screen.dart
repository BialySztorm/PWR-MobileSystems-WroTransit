import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/stops_repository.dart';

class StopDetailScreen extends ConsumerWidget {
  const StopDetailScreen({super.key, required this.stopId});

  final int stopId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stopAsync = ref.watch(stopProvider(stopId));
    final linesAsync = ref.watch(stopLinesProvider(stopId));

    return Scaffold(
      appBar: AppBar(
        title: stopAsync.when(
          data: (stop) => Text(stop.name),
          loading: () => const Text('Stop'),
          error: (_, __) => const Text('Stop'),
        ),
      ),
      body: linesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Failed to load lines: $error')),
        data: (lines) => ListView(
          children: [
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text('Lines serving this stop', style: TextStyle(fontWeight: FontWeight.bold)),
            ),
            if (lines.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: Text('No lines found for this stop.'),
              ),
            for (final line in lines)
              ListTile(
                leading: const Icon(Icons.directions_bus),
                title: Text('${line.code} · ${line.name}'),
              ),
          ],
        ),
      ),
    );
  }
}
