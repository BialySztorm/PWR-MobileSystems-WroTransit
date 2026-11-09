import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../favourites/data/favourites_controller.dart';
import '../data/stops_repository.dart';

class StopsScreen extends ConsumerStatefulWidget {
  const StopsScreen({super.key});

  @override
  ConsumerState<StopsScreen> createState() => _StopsScreenState();
}

class _StopsScreenState extends ConsumerState<StopsScreen> {
  Timer? _debounce;

  void _onQueryChanged(String value) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 300), () {
      ref.read(stopsSearchQueryProvider.notifier).state = value;
    });
  }

  @override
  void dispose() {
    _debounce?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final stopsAsync = ref.watch(stopsListProvider);
    final favourites = ref.watch(favouritesControllerProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Stops')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              decoration: const InputDecoration(
                hintText: 'Search stops',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onChanged: _onQueryChanged,
            ),
          ),
          Expanded(
            child: stopsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(child: Text('Failed to load stops: $error')),
              data: (stops) => ListView.builder(
                itemCount: stops.length,
                itemBuilder: (context, index) {
                  final stop = stops[index];
                  final isFavourite =
                      favourites.contains(FavouriteId(FavouriteKind.stop, stop.stopId));
                  return ListTile(
                    title: Text(stop.name),
                    trailing: IconButton(
                      icon: Icon(isFavourite ? Icons.favorite : Icons.favorite_border),
                      onPressed: () => ref
                          .read(favouritesControllerProvider.notifier)
                          .toggle(FavouriteKind.stop, stop.stopId),
                    ),
                    onTap: () => context.push('/stops/${stop.stopId}'),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
