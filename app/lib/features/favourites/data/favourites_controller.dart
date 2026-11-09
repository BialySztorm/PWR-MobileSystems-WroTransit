import 'package:flutter_riverpod/flutter_riverpod.dart';

enum FavouriteKind { stop, line }

class FavouriteId {
  const FavouriteId(this.kind, this.id);

  final FavouriteKind kind;
  final String id;

  @override
  bool operator ==(Object other) =>
      other is FavouriteId && other.kind == kind && other.id == id;

  @override
  int get hashCode => Object.hash(kind, id);
}

class FavouritesController extends StateNotifier<Set<FavouriteId>> {
  FavouritesController() : super(<FavouriteId>{});

  bool isFavourite(FavouriteKind kind, String id) => state.contains(FavouriteId(kind, id));

  void toggle(FavouriteKind kind, String id) {
    final favouriteId = FavouriteId(kind, id);
    final next = Set<FavouriteId>.from(state);
    if (!next.remove(favouriteId)) {
      next.add(favouriteId);
    }
    state = next;
  }
}

final favouritesControllerProvider =
    StateNotifierProvider<FavouritesController, Set<FavouriteId>>(
  (ref) => FavouritesController(),
);
