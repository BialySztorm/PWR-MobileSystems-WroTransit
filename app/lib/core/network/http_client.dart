import 'dart:io';

class AppHttpClient {
  AppHttpClient._();

  static HttpClient create() {
    return HttpClient();
  }
}
