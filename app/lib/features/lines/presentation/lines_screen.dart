import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../favourites/data/favourites_controller.dart';
import '../data/lines_repository.dart';

class LinesScreen extends ConsumerStatefulWidget {
  const LinesScreen({super.key});

  @override
  ConsumerState<LinesScreen> createState() => _LinesScreenState();
}

class _LinesScreenState extends ConsumerState<LinesScreen> {
  Timer? _debounce;

  void _onQueryChanged(String value) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 300), () {
      ref.read(linesSearchQueryProvider.notifier).state = value;
    });
  }

  @override
  void dispose() {
    _debounce?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final linesAsync = ref.watch(linesListProvider);
    final favourites = ref.watch(favouritesControllerProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Lines')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              decoration: const InputDecoration(
                hintText: 'Search lines',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onChanged: _onQueryChanged,
            ),
          ),
          Expanded(
            child: linesAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(child: Text('Failed to load lines: $error')),
              data: (lines) => ListView.builder(
                itemCount: lines.length,
                itemBuilder: (context, index) {
                  final line = lines[index];
                  final isFavourite =
                      favourites.contains(FavouriteId(FavouriteKind.line, line.routeId));
                  return ListTile(
                    leading: Icon(line.isTram ? Icons.tram : Icons.directions_bus),
                    title: Text(line.longName ?? line.shortName),
                    subtitle: Text(line.shortName),
                    trailing: IconButton(
                      icon: Icon(isFavourite ? Icons.favorite : Icons.favorite_border),
                      onPressed: () => ref
                          .read(favouritesControllerProvider.notifier)
                          .toggle(FavouriteKind.line, line.routeId),
                    ),
                    onTap: () => context.push('/lines/${line.routeId}'),
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
