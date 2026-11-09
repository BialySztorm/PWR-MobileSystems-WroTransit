class Vehicle {
  const Vehicle({
    required this.vehicleId,
    required this.line,
    required this.lat,
    required this.lon,
    required this.recordedAt,
    required this.delayS,
  });

  final String vehicleId;
  final String? line;
  final double? lat;
  final double? lon;
  final DateTime? recordedAt;
  final int? delayS;

  factory Vehicle.fromJson(Map<String, dynamic> json) => Vehicle(
        vehicleId: json['vehicle_id'] as String,
        line: json['line'] as String?,
        lat: (json['lat'] as num?)?.toDouble(),
        lon: (json['lon'] as num?)?.toDouble(),
        recordedAt: json['recorded_at'] == null
            ? null
            : DateTime.parse(json['recorded_at'] as String),
        delayS: json['delay_s'] as int?,
      );
}
