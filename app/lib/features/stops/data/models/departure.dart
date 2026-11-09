class Departure {
  const Departure({
    required this.routeShortName,
    required this.routeType,
    required this.headsign,
    required this.directionId,
    required this.departureTimeS,
  });

  final String routeShortName;
  final int routeType;
  final String? headsign;
  final int? directionId;
  final int departureTimeS;

  bool get isTram => routeType == 0;

  String get formattedTime {
    final totalMinutes = departureTimeS ~/ 60;
    final hours = (totalMinutes ~/ 60) % 24;
    final minutes = totalMinutes % 60;
    return '${hours.toString().padLeft(2, '0')}:${minutes.toString().padLeft(2, '0')}';
  }

  factory Departure.fromJson(Map<String, dynamic> json) => Departure(
        routeShortName: json['route_short_name'] as String,
        routeType: json['route_type'] as int,
        headsign: json['headsign'] as String?,
        directionId: json['direction_id'] as int?,
        departureTimeS: json['departure_time_s'] as int,
      );
}
