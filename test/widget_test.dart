// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:rural_education/main.dart';

void main() {
  testWidgets('App loads and shows initial screen',
      (WidgetTester tester) async {
    // Build the app
    await tester.pumpWidget(const MyApp());

    // While SharedPreferences loads, CircularProgressIndicator should show
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    // Let Flutter settle
    await tester.pumpAndSettle();

    // After prefs load, either LoginScreen or HomeScreen should be displayed
    final loginScreenFound = find.textContaining('Login').evaluate().isNotEmpty;
    final homeScreenFound = find.textContaining('Home').evaluate().isNotEmpty;

    expect(loginScreenFound || homeScreenFound, true,
        reason: 'Either LoginScreen or HomeScreen should appear');
  });
}
