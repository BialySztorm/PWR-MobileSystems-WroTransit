class Vehicle {
  const Vehicle({
    required this.id,
    required this.lineId,
    required this.label,
    required this.lat,
    required this.lon,
    required this.updatedAt,
  });

  final int id;
  final int lineId;
  final String label;
  final double lat;
  final double lon;
  final DateTime updatedAt;

  factory Vehicle.fromJson(Map<String, dynamic> json) => Vehicle(
        id: json['id'] as int,
        lineId: json['line_id'] as int,
        label: json['label'] as String,
        lat: (json['lat'] as num).toDouble(),
        lon: (json['lon'] as num).toDouble(),
        updatedAt: DateTime.parse(json['updated_at'] as String),
      );
}
