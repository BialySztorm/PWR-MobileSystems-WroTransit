import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';

class ApiException implements Exception {
  ApiException(this.statusCode, this.message);

  final int statusCode;
  final String message;

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class ApiClient {
  ApiClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Future<dynamic> get(String path, {Map<String, String>? query}) async {
    final uri = Uri.parse('${AppConfig.apiBaseUrl}$path').replace(
      queryParameters: query,
    );
    final response = await _client.get(uri);

    if (response.statusCode >= 400) {
      throw ApiException(response.statusCode, response.body);
    }

    return jsonDecode(response.body);
  }

  Future<List<dynamic>> getList(String path, {Map<String, String>? query}) async {
    final result = await get(path, query: query);
    return result as List<dynamic>;
  }
}
