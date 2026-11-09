import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/profile_screen.dart';
import '../../features/favourites/presentation/favourites_screen.dart';
import '../../features/lines/presentation/line_detail_screen.dart';
import '../../features/lines/presentation/lines_screen.dart';
import '../../features/map/presentation/map_screen.dart';
import '../../features/stops/presentation/stop_detail_screen.dart';
import '../../features/stops/presentation/stops_screen.dart';

class AppRouter {
  const AppRouter._();

  static final router = GoRouter(
    initialLocation: '/map',
    routes: [
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return _RootScaffold(navigationShell: navigationShell);
        },
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/map',
                builder: (context, state) => const MapScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/stops',
                builder: (context, state) => const StopsScreen(),
                routes: [
                  GoRoute(
                    path: ':id',
                    builder: (context, state) => StopDetailScreen(
                      stopId: int.parse(state.pathParameters['id']!),
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/lines',
                builder: (context, state) => const LinesScreen(),
                routes: [
                  GoRoute(
                    path: ':id',
                    builder: (context, state) => LineDetailScreen(
                      lineId: int.parse(state.pathParameters['id']!),
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/favourites',
                builder: (context, state) => const FavouritesScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/profile',
                builder: (context, state) => const ProfileScreen(),
              ),
            ],
          ),
        ],
      ),
    ],
  );
}

class _RootScaffold extends StatelessWidget {
  const _RootScaffold({required this.navigationShell});

  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: navigationShell.currentIndex,
        onTap: (index) {
          navigationShell.goBranch(
            index,
            initialLocation: index == navigationShell.currentIndex,
          );
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Map'),
          BottomNavigationBarItem(icon: Icon(Icons.place), label: 'Stops'),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_bus),
            label: 'Lines',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.favorite),
            label: 'Favourites',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
