import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../favourites/data/favourites_controller.dart';
import '../data/lines_repository.dart';

class LinesScreen extends ConsumerWidget {
  const LinesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final linesAsync = ref.watch(linesListProvider);
    final favourites = ref.watch(favouritesControllerProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Lines')),
      body: linesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Failed to load lines: $error')),
        data: (lines) => ListView.builder(
          itemCount: lines.length,
          itemBuilder: (context, index) {
            final line = lines[index];
            final isFavourite = favourites.contains(FavouriteId(FavouriteKind.line, line.id));
            return ListTile(
              title: Text('${line.code} · ${line.name}'),
              trailing: IconButton(
                icon: Icon(isFavourite ? Icons.favorite : Icons.favorite_border),
                onPressed: () => ref
                    .read(favouritesControllerProvider.notifier)
                    .toggle(FavouriteKind.line, line.id),
              ),
              onTap: () => context.push('/lines/${line.id}'),
            );
          },
        ),
      ),
    );
  }
}
