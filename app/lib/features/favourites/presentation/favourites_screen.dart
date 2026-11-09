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
        favourites.where((f) => f.kind == FavouriteKind.stop).map((f) => f.id).toList();
    final favouriteLineIds =
        favourites.where((f) => f.kind == FavouriteKind.line).map((f) => f.id).toList();

    return Scaffold(
      appBar: AppBar(title: const Text('Favourites')),
      body: ListView(
        children: [
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text('Stops', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
          if (favouriteStopIds.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Text('No favourite stops yet.'),
            )
          else
            for (final stopId in favouriteStopIds) _FavouriteStopTile(stopId: stopId),
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text('Lines', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
          if (favouriteLineIds.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Text('No favourite lines yet.'),
            )
          else
            for (final lineId in favouriteLineIds) _FavouriteLineTile(lineId: lineId),
        ],
      ),
    );
  }
}

class _FavouriteStopTile extends ConsumerWidget {
  const _FavouriteStopTile({required this.stopId});

  final String stopId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stopAsync = ref.watch(stopProvider(stopId));
    return stopAsync.when(
      loading: () => const ListTile(leading: Icon(Icons.place), title: Text('Loading...')),
      error: (error, _) => ListTile(
        leading: const Icon(Icons.place),
        title: Text('Failed to load stop: $error'),
      ),
      data: (stop) => ListTile(leading: const Icon(Icons.place), title: Text(stop.name)),
    );
  }
}

class _FavouriteLineTile extends ConsumerWidget {
  const _FavouriteLineTile({required this.lineId});

  final String lineId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lineAsync = ref.watch(lineProvider(lineId));
    return lineAsync.when(
      loading: () =>
          const ListTile(leading: Icon(Icons.directions_bus), title: Text('Loading...')),
      error: (error, _) => ListTile(
        leading: const Icon(Icons.directions_bus),
        title: Text('Failed to load line: $error'),
      ),
      data: (line) => ListTile(
        leading: Icon(line.isTram ? Icons.tram : Icons.directions_bus),
        title: Text('${line.shortName} · ${line.longName ?? line.shortName}'),
      ),
    );
  }
}
