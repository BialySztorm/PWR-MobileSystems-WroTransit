import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../lines/data/lines_repository.dart';
import '../../stops/data/stops_repository.dart';
import '../data/favourites_controller.dart';

class FavouritesScreen extends ConsumerWidget {
  const FavouritesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final favourites = ref.watch(favouritesControllerProvider);
    final favouriteStopIds =
        favourites.where((f) => f.kind == FavouriteKind.stop).map((f) => f.id).toSet();
    final favouriteLineIds =
        favourites.where((f) => f.kind == FavouriteKind.line).map((f) => f.id).toSet();

    final stopsAsync = ref.watch(stopsListProvider);
    final linesAsync = ref.watch(linesListProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Favourites')),
      body: ListView(
        children: [
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text('Stops', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
          stopsAsync.when(
            loading: () => const LinearProgressIndicator(),
            error: (error, _) => Text('Failed to load stops: $error'),
            data: (stops) {
              final favouriteStops =
                  stops.where((s) => favouriteStopIds.contains(s.id)).toList();
              if (favouriteStops.isEmpty) {
                return const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: Text('No favourite stops yet.'),
                );
              }
              return Column(
                children: [
                  for (final stop in favouriteStops)
                    ListTile(leading: const Icon(Icons.place), title: Text(stop.name)),
                ],
              );
            },
          ),
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text('Lines', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
          linesAsync.when(
            loading: () => const LinearProgressIndicator(),
            error: (error, _) => Text('Failed to load lines: $error'),
            data: (lines) {
              final favouriteLines =
                  lines.where((l) => favouriteLineIds.contains(l.id)).toList();
              if (favouriteLines.isEmpty) {
                return const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: Text('No favourite lines yet.'),
                );
              }
              return Column(
                children: [
                  for (final line in favouriteLines)
                    ListTile(
                      leading: const Icon(Icons.directions_bus),
                      title: Text('${line.code} · ${line.name}'),
                    ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}
