import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/stops_repository.dart';

class StopDetailScreen extends ConsumerWidget {
  const StopDetailScreen({super.key, required this.stopId});

  final String stopId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stopAsync = ref.watch(stopProvider(stopId));
    final departuresAsync = ref.watch(stopDeparturesProvider(stopId));

    return Scaffold(
      appBar: AppBar(
        title: stopAsync.when(
          data: (stop) => Text(stop.name),
          loading: () => const Text('Stop'),
          error: (_, __) => const Text('Stop'),
        ),
      ),
      body: departuresAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Failed to load departures: $error')),
        data: (departures) {
          if (departures.isEmpty) {
            return const Center(child: Text('No upcoming departures.'));
          }
          return ListView.builder(
            itemCount: departures.length,
            itemBuilder: (context, index) {
              final departure = departures[index];
              return ListTile(
                leading: CircleAvatar(
                  child: Icon(departure.isTram ? Icons.tram : Icons.directions_bus),
                ),
                title: Text(
                  '${departure.routeShortName}'
                  '${departure.headsign != null ? ' → ${departure.headsign}' : ''}',
                ),
                trailing: Text(
                  departure.formattedTime,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
