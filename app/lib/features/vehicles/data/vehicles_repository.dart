import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/providers.dart';
import 'models/vehicle.dart';

class VehiclesRepository {
  VehiclesRepository(this._ref);

  final Ref _ref;

  Future<List<Vehicle>> getVehicles({int? lineId}) async {
    final api = _ref.read(apiClientProvider);
    final list = await api.getList(
      '/vehicles',
      query: lineId == null ? null : {'line_id': '$lineId'},
    );
    return list.map((e) => Vehicle.fromJson(e as Map<String, dynamic>)).toList();
  }
}

final vehiclesRepositoryProvider =
    Provider<VehiclesRepository>((ref) => VehiclesRepository(ref));

final vehiclesForLineProvider = FutureProvider.family<List<Vehicle>, int>((ref, lineId) {
  return ref.read(vehiclesRepositoryProvider).getVehicles(lineId: lineId);
});
