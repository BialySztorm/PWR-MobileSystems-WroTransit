import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/providers.dart';
import 'models/departure.dart';
import 'models/stop.dart';

class StopsRepository {
  StopsRepository(this._ref);

  final Ref _ref;

  Future<List<Stop>> getStops({String? query}) async {
    final api = _ref.read(apiClientProvider);
    final list = await api.getList(
      '/stops',
      query: (query == null || query.isEmpty) ? null : {'q': query},
    );
    return list.map((e) => Stop.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<Stop>> getStopsInBbox(String bbox) async {
    final api = _ref.read(apiClientProvider);
    final list = await api.getList('/stops', query: {'bbox': bbox});
    return list.map((e) => Stop.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Stop> getStop(String id) async {
    final api = _ref.read(apiClientProvider);
    final json = await api.get('/stops/$id');
    return Stop.fromJson(json as Map<String, dynamic>);
  }

  Future<List<Departure>> getDepartures(String stopId) async {
    final api = _ref.read(apiClientProvider);
    final list = await api.getList('/stops/$stopId/departures');
    return list.map((e) => Departure.fromJson(e as Map<String, dynamic>)).toList();
  }
}

final stopsRepositoryProvider = Provider<StopsRepository>((ref) => StopsRepository(ref));

final stopsSearchQueryProvider = StateProvider<String>((ref) => '');

final stopsListProvider = FutureProvider<List<Stop>>((ref) {
  final query = ref.watch(stopsSearchQueryProvider);
  return ref.read(stopsRepositoryProvider).getStops(query: query);
});

final stopProvider = FutureProvider.family<Stop, String>((ref, id) {
  return ref.read(stopsRepositoryProvider).getStop(id);
});

final stopDeparturesProvider = FutureProvider.family<List<Departure>, String>((ref, stopId) {
  return ref.read(stopsRepositoryProvider).getDepartures(stopId);
});
