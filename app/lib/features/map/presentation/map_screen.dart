import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

import '../../lines/data/models/shape.dart';
import '../../lines/data/shapes_repository.dart';
import '../../stops/data/models/stop.dart';
import '../../stops/data/stops_repository.dart';

class MapScreen extends ConsumerStatefulWidget {
  const MapScreen({super.key});

  @override
  ConsumerState<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends ConsumerState<MapScreen> {
  static const _wroclawCenter = LatLng(51.107883, 17.038538);

  final _mapController = MapController();
  StreamSubscription<MapEvent>? _mapEventSub;
  Timer? _debounce;

  bool _showTrams = true;
  bool _showBuses = true;
  LatLng? _userPosition;
  String? _locationError;

  List<Stop> _stops = [];
  List<Shape> _shapes = [];

  @override
  void initState() {
    super.initState();
    _mapEventSub = _mapController.mapEventStream.listen((event) {
      if (event is MapEventMoveEnd || event is MapEventFlingAnimationEnd) {
        _scheduleFetch();
      }
    });
    WidgetsBinding.instance.addPostFrameCallback((_) => _fetchViewportData());
  }

  @override
  void dispose() {
    _mapEventSub?.cancel();
    _debounce?.cancel();
    super.dispose();
  }

  void _scheduleFetch() {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 400), _fetchViewportData);
  }

  Future<void> _fetchViewportData() async {
    final bounds = _mapController.camera.visibleBounds;
    final bbox =
        '${bounds.southWest.longitude},${bounds.southWest.latitude},'
        '${bounds.northEast.longitude},${bounds.northEast.latitude}';

    try {
      final stops = await ref.read(stopsRepositoryProvider).getStopsInBbox(bbox);
      final shapes = await ref.read(shapesRepositoryProvider).getShapesInBbox(bbox);
      if (!mounted) return;
      setState(() {
        _stops = stops;
        _shapes = shapes;
      });
    } catch (_) {
      // Viewport data is a nice-to-have overlay; silently keep the previous markers on failure.
    }
  }

  Future<void> _locateUser() async {
    if (!await Geolocator.isLocationServiceEnabled()) {
      setState(() => _locationError = 'Location services are disabled.');
      return;
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      setState(() => _locationError = 'Location permission denied.');
      return;
    }

    final position = await Geolocator.getCurrentPosition();
    final userLatLng = LatLng(position.latitude, position.longitude);
    setState(() {
      _userPosition = userLatLng;
      _locationError = null;
    });
    _mapController.move(userLatLng, 15);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          FlutterMap(
            mapController: _mapController,
            options: const MapOptions(
              initialCenter: _wroclawCenter,
              initialZoom: 14,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'pl.edu.pwr.wrotransit',
              ),
              PolylineLayer(
                polylines: [
                  for (final shape in _shapes)
                    if ((shape.isTram && _showTrams) ||
                        (shape.isBus && _showBuses) ||
                        (!shape.isTram && !shape.isBus))
                      Polyline(
                        points: shape.points,
                        strokeWidth: 3,
                        color: shape.isTram ? Colors.red : Colors.indigo,
                      ),
                ],
              ),
              MarkerLayer(
                markers: [
                  for (final stop in _stops)
                    Marker(
                      point: LatLng(stop.lat, stop.lon),
                      width: 14,
                      height: 14,
                      child: _StopMarker(stop: stop),
                    ),
                  if (_userPosition != null)
                    Marker(
                      point: _userPosition!,
                      child: const Icon(Icons.my_location, color: Colors.blue),
                    ),
                ],
              ),
            ],
          ),
          Positioned(
            top: 12,
            left: 12,
            right: 12,
            child: Column(
              children: [
                const TextField(
                  decoration: InputDecoration(
                    hintText: 'Search line or stop',
                    prefixIcon: Icon(Icons.search),
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(borderSide: BorderSide.none),
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    FilterChip(
                      label: const Text('Trams'),
                      avatar: const Icon(Icons.tram, size: 18),
                      selected: _showTrams,
                      onSelected: (value) => setState(() => _showTrams = value),
                    ),
                    const SizedBox(width: 8),
                    FilterChip(
                      label: const Text('Buses'),
                      avatar: const Icon(Icons.directions_bus, size: 18),
                      selected: _showBuses,
                      onSelected: (value) => setState(() => _showBuses = value),
                    ),
                  ],
                ),
                if (_locationError != null) ...[
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(_locationError!, style: const TextStyle(color: Colors.red)),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _locateUser,
        child: const Icon(Icons.my_location),
      ),
    );
  }
}

/// A small white dot with a coloured ring: red for tram-only, indigo for bus-only, purple
/// when a stop serves both, grey when the mode isn't known yet.
class _StopMarker extends StatelessWidget {
  const _StopMarker({required this.stop});

  final Stop stop;

  @override
  Widget build(BuildContext context) {
    final Color ringColor;
    if (stop.servesTram && stop.servesBus) {
      ringColor = Colors.purple;
    } else if (stop.servesTram) {
      ringColor = Colors.red;
    } else if (stop.servesBus) {
      ringColor = Colors.indigo;
    } else {
      ringColor = Colors.grey;
    }

    return Container(
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: Colors.white,
        border: Border.all(color: ringColor, width: 2),
      ),
    );
  }
}
