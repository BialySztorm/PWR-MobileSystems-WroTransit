import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/providers.dart';
import 'models/shape.dart';

class ShapesRepository {
  ShapesRepository(this._ref);

  final Ref _ref;

  Future<List<Shape>> getShapesInBbox(String bbox) async {
    final api = _ref.read(apiClientProvider);
    final list = await api.getList('/shapes', query: {'bbox': bbox});
    return list.map((e) => Shape.fromJson(e as Map<String, dynamic>)).toList();
  }
}

final shapesRepositoryProvider = Provider<ShapesRepository>((ref) => ShapesRepository(ref));
