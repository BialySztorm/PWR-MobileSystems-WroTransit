import '../../../stops/data/models/stop.dart';

class RouteStop {
  const RouteStop({required this.sequence, required this.stop});

  final int sequence;
  final Stop stop;

  factory RouteStop.fromJson(Map<String, dynamic> json) => RouteStop(
        sequence: json['sequence'] as int,
        stop: Stop.fromJson(json['stop'] as Map<String, dynamic>),
      );
}

class LineRoute {
  const LineRoute({required this.routeId, required this.directionId, required this.stops});

  final String routeId;
  final int? directionId;
  final List<RouteStop> stops;

  factory LineRoute.fromJson(Map<String, dynamic> json) => LineRoute(
        routeId: json['route_id'] as String,
        directionId: json['direction_id'] as int?,
        stops: (json['stops'] as List<dynamic>)
            .map((e) => RouteStop.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}
