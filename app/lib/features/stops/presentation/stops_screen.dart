import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../favourites/data/favourites_controller.dart';
import '../data/stops_repository.dart';

class StopsScreen extends ConsumerWidget {
  const StopsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stopsAsync = ref.watch(stopsListProvider);
    final favourites = ref.watch(favouritesControllerProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Stops')),
      body: stopsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Failed to load stops: $error')),
        data: (stops) => ListView.builder(
          itemCount: stops.length,
          itemBuilder: (context, index) {
            final stop = stops[index];
            final isFavourite = favourites.contains(FavouriteId(FavouriteKind.stop, stop.id));
            return ListTile(
              title: Text(stop.name),
              trailing: IconButton(
                icon: Icon(isFavourite ? Icons.favorite : Icons.favorite_border),
                onPressed: () => ref
                    .read(favouritesControllerProvider.notifier)
                    .toggle(FavouriteKind.stop, stop.id),
              ),
              onTap: () => context.push('/stops/${stop.id}'),
            );
          },
        ),
      ),
    );
  }
}
