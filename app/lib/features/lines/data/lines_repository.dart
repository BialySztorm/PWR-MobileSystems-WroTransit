import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/providers.dart';
import 'models/line.dart';
import 'models/line_route.dart';

class LinesRepository {
  LinesRepository(this._ref);

  final Ref _ref;

  Future<List<Line>> getLines() async {
    final api = _ref.read(apiClientProvider);
    final list = await api.getList('/lines');
    return list.map((e) => Line.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Line> getLine(int id) async {
    final api = _ref.read(apiClientProvider);
    final json = await api.get('/lines/$id');
    return Line.fromJson(json as Map<String, dynamic>);
  }

  Future<LineRoute> getLineRoute(int id) async {
    final api = _ref.read(apiClientProvider);
    final json = await api.get('/lines/$id/route');
    return LineRoute.fromJson(json as Map<String, dynamic>);
  }
}

final linesRepositoryProvider = Provider<LinesRepository>((ref) => LinesRepository(ref));

final linesListProvider = FutureProvider<List<Line>>((ref) {
  return ref.read(linesRepositoryProvider).getLines();
});

final lineProvider = FutureProvider.family<Line, int>((ref, id) {
  return ref.read(linesRepositoryProvider).getLine(id);
});

final lineRouteProvider = FutureProvider.family<LineRoute, int>((ref, id) {
  return ref.read(linesRepositoryProvider).getLineRoute(id);
});
