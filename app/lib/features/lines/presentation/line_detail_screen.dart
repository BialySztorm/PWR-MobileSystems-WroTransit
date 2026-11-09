import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/lines_repository.dart';

class LineDetailScreen extends ConsumerWidget {
  const LineDetailScreen({super.key, required this.lineId});

  final int lineId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lineAsync = ref.watch(lineProvider(lineId));
    final routeAsync = ref.watch(lineRouteProvider(lineId));

    return Scaffold(
      appBar: AppBar(
        title: lineAsync.when(
          data: (line) => Text('${line.code} · ${line.name}'),
          loading: () => const Text('Line'),
          error: (_, __) => const Text('Line'),
        ),
      ),
      body: routeAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Failed to load route: $error')),
        data: (route) => ListView.builder(
          itemCount: route.stops.length,
          itemBuilder: (context, index) {
            final routeStop = route.stops[index];
            return ListTile(
              leading: CircleAvatar(child: Text('${index + 1}')),
              title: Text(routeStop.stop.name),
            );
          },
        ),
      ),
    );
  }
}
