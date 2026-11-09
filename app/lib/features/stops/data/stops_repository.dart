import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/providers.dart';
import '../../lines/data/models/line.dart';
import 'models/stop.dart';

class StopsRepository {
  StopsRepository(this._ref);

  final Ref _ref;

  Future<List<Stop>> getStops() async {
    final api = _ref.read(apiClientProvider);
    final list = await api.getList('/stops');
    return list.map((e) => Stop.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Stop> getStop(int id) async {
    final api = _ref.read(apiClientProvider);
    final json = await api.get('/stops/$id');
    return Stop.fromJson(json as Map<String, dynamic>);
  }

  Future<List<Line>> getLinesForStop(int id) async {
    final api = _ref.read(apiClientProvider);
    final list = await api.getList('/stops/$id/lines');
    return list.map((e) => Line.fromJson(e as Map<String, dynamic>)).toList();
  }
}

final stopsRepositoryProvider = Provider<StopsRepository>((ref) => StopsRepository(ref));

final stopsListProvider = FutureProvider<List<Stop>>((ref) {
  return ref.read(stopsRepositoryProvider).getStops();
});

final stopProvider = FutureProvider.family<Stop, int>((ref, id) {
  return ref.read(stopsRepositoryProvider).getStop(id);
});

final stopLinesProvider = FutureProvider.family<List<Line>, int>((ref, id) {
  return ref.read(stopsRepositoryProvider).getLinesForStop(id);
});
