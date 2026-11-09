import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/providers.dart';
import 'models/line.dart';
import 'models/line_route.dart';

class LinesRepository {
  LinesRepository(this._ref);

  final Ref _ref;

  Future<List<Line>> getLines({String? query}) async {
    final api = _ref.read(apiClientProvider);
    final list = await api.getList(
      '/routes',
      query: (query == null || query.isEmpty) ? null : {'q': query},
    );
    return list.map((e) => Line.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Line> getLine(String id) async {
    final api = _ref.read(apiClientProvider);
    final json = await api.get('/routes/$id');
    return Line.fromJson(json as Map<String, dynamic>);
  }

  Future<LineRoute> getLineRoute(String id) async {
    final api = _ref.read(apiClientProvider);
    final json = await api.get('/routes/$id/route');
    return LineRoute.fromJson(json as Map<String, dynamic>);
  }
}

final linesRepositoryProvider = Provider<LinesRepository>((ref) => LinesRepository(ref));

final linesSearchQueryProvider = StateProvider<String>((ref) => '');

final linesListProvider = FutureProvider<List<Line>>((ref) {
  final query = ref.watch(linesSearchQueryProvider);
  return ref.read(linesRepositoryProvider).getLines(query: query);
});

final lineProvider = FutureProvider.family<Line, String>((ref, id) {
  return ref.read(linesRepositoryProvider).getLine(id);
});

final lineRouteProvider = FutureProvider.family<LineRoute, String>((ref, id) {
  return ref.read(linesRepositoryProvider).getLineRoute(id);
});
