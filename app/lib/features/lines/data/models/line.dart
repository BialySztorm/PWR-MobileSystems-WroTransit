class Line {
  const Line({
    required this.id,
    required this.code,
    required this.name,
    this.color,
  });

  final int id;
  final String code;
  final String name;
  final String? color;

  factory Line.fromJson(Map<String, dynamic> json) => Line(
        id: json['id'] as int,
        code: json['code'] as String,
        name: json['name'] as String,
        color: json['color'] as String?,
      );
}
