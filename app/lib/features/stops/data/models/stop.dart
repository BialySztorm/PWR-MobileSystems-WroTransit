class Stop {
  const Stop({
    required this.stopId,
    required this.stopCode,
    required this.name,
    required this.lat,
    required this.lon,
    required this.modes,
  });

  final String stopId;
  final String? stopCode;
  final String name;
  final double lat;
  final double lon;

  /// Distinct GTFS route_type values served here: 0 = tram, 3 = bus. Only populated when
  /// fetched with a bbox (map viewport); empty for plain search results.
  final List<int> modes;

  bool get servesTram => modes.contains(0);
  bool get servesBus => modes.contains(3);

  factory Stop.fromJson(Map<String, dynamic> json) => Stop(
        stopId: json['stop_id'] as String,
        stopCode: json['stop_code'] as String?,
        name: json['name'] as String,
        lat: (json['lat'] as num).toDouble(),
        lon: (json['lon'] as num).toDouble(),
        modes: (json['modes'] as List<dynamic>? ?? []).map((e) => e as int).toList(),
      );
}
