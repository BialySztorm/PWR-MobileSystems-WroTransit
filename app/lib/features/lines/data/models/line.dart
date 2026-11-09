class Line {
  const Line({
    required this.routeId,
    required this.shortName,
    required this.longName,
    required this.type,
  });

  final String routeId;
  final String shortName;
  final String? longName;
  final int type;

  bool get isTram => type == 0;

  factory Line.fromJson(Map<String, dynamic> json) => Line(
        routeId: json['route_id'] as String,
        shortName: json['short_name'] as String,
        longName: json['long_name'] as String?,
        type: json['type'] as int,
      );
}
