class Stop {
  const Stop({
    required this.id,
    required this.name,
    required this.lat,
    required this.lon,
  });

  final int id;
  final String name;
  final double lat;
  final double lon;

  factory Stop.fromJson(Map<String, dynamic> json) => Stop(
        id: json['id'] as int,
        name: json['name'] as String,
        lat: (json['lat'] as num).toDouble(),
        lon: (json['lon'] as num).toDouble(),
      );
}
