class AnalyticsProviderConfig {
  const AnalyticsProviderConfig({
    required this.provider,
    required this.apiKey,
    this.host = '',
    this.options = const <String, Object>{},
  });

  final String provider;
  final String apiKey;
  final String host;
  final Map<String, Object> options;
}
