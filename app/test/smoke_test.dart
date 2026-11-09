import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:wrotransit_app/main.dart';

void main() {
  testWidgets('app starts on Map tab with all five navigation tabs', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: WroTransitApp()));
    await tester.pump();

    expect(find.byType(BottomNavigationBar), findsOneWidget);
    expect(find.text('Map'), findsOneWidget);
    expect(find.text('Stops'), findsOneWidget);
    expect(find.text('Lines'), findsOneWidget);
    expect(find.text('Favourites'), findsOneWidget);
    expect(find.text('Profile'), findsOneWidget);
  });
}
