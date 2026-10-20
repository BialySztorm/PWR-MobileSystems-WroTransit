import 'package:flutter/material.dart';

import 'core/routing/app_router.dart';
import 'core/theme/app_theme.dart';

void main() {
  runApp(const WroTransitApp());
}

class WroTransitApp extends StatelessWidget {
  const WroTransitApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'WroTransit',
      theme: AppTheme.light,
      routerConfig: AppRouter.router,
    );
  }
}
