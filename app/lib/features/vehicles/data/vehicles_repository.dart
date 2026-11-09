import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/providers.dart';
import 'models/vehicle.dart';

class VehiclesRepository {
  VehiclesRepository(this._ref);

  final Ref _ref;

  Future<List<Vehicle>> getVehicles({String? line}) async {
    final api = _ref.read(apiClientProvider);
    final list = await api.getList(
      '/vehicles',
      query: line == null ? null : {'line': line},
    );
    return list.map((e) => Vehicle.fromJson(e as Map<String, dynamic>)).toList();
  }
}

final vehiclesRepositoryProvider =
    Provider<VehiclesRepository>((ref) => VehiclesRepository(ref));

final vehiclesForLineProvider = FutureProvider.family<List<Vehicle>, String>((ref, line) {
  return ref.read(vehiclesRepositoryProvider).getVehicles(line: line);
});
