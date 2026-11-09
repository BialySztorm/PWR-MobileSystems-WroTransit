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
  const LineRoute({required this.id, required this.lineId, required this.stops});

  final int id;
  final int lineId;
  final List<RouteStop> stops;

  factory LineRoute.fromJson(Map<String, dynamic> json) => LineRoute(
        id: json['id'] as int,
        lineId: json['line_id'] as int,
        stops: (json['stops'] as List<dynamic>)
            .map((e) => RouteStop.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}
