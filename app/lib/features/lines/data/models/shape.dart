import 'package:latlong2/latlong.dart';

class Shape {
  const Shape({required this.shapeId, required this.points, required this.routeType});

  final String shapeId;
  final List<LatLng> points;
  final int? routeType;

  bool get isTram => routeType == 0;
  bool get isBus => routeType == 3;

  factory Shape.fromJson(Map<String, dynamic> json) {
    final coordinates = json['coordinates'] as List<dynamic>;
    return Shape(
      shapeId: json['shape_id'] as String,
      points: coordinates
          .map((c) => LatLng((c[1] as num).toDouble(), (c[0] as num).toDouble()))
          .toList(),
      routeType: json['route_type'] as int?,
    );
  }
}
