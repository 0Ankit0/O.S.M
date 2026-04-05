import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'analytics_base.dart';
import 'analytics_interface.dart';
import 'analytics_service.dart';
import 'adapters/mixpanel_adapter.dart';
import 'adapters/posthog_adapter.dart';

/// Riverpod provider for [AnalyticsService].
///
/// Usage anywhere in the app:
/// ```dart
/// final analytics = ref.read(analyticsServiceProvider);
/// await analytics.capture('my_event');
/// ```
///
/// The provider reads `ANALYTICS_ENABLED` and `ANALYTICS_PROVIDER` from .env.
/// Add new providers to the factory block below — no other files need changing.
final analyticsServiceProvider = Provider<AnalyticsService>((ref) {
  // Return a no-op service if analytics is not yet initialised.
  // The actual service is injected in main() via ProviderContainer overrides.
  return const AnalyticsService(null);
});

/// Call this once in main() before runApp().
///
/// Returns an [AnalyticsService] that should override [analyticsServiceProvider].
///
/// Example:
/// ```dart
/// final analytics = await buildAnalyticsService();
/// runApp(ProviderScope(
///   overrides: [analyticsServiceProvider.overrideWithValue(analytics)],
///   child: App(),
/// ));
/// ```
Future<AnalyticsService> buildAnalyticsService() async {
  final enabled = dotenv.env['ANALYTICS_ENABLED']?.toLowerCase() == 'true';
  if (!enabled) return const AnalyticsService(null);

  final config = _resolveAnalyticsConfig();
  if (config == null) return const AnalyticsService(null);
  final builder = _registry[config.provider];
  if (builder == null) return const AnalyticsService(null);
  final adapter = await builder(config);
  return AnalyticsService(adapter);
}

AnalyticsProviderConfig? _resolveAnalyticsConfig() {
  final provider = dotenv.env['ANALYTICS_PROVIDER']?.toLowerCase() ?? 'posthog';
  var apiKey = dotenv.env['ANALYTICS_API_KEY'] ?? '';
  var host = dotenv.env['ANALYTICS_HOST'] ?? '';

  if (provider == 'posthog') {
    apiKey = apiKey.isNotEmpty ? apiKey : (dotenv.env['POSTHOG_API_KEY'] ?? '');
    host = host.isNotEmpty ? host : (dotenv.env['POSTHOG_HOST'] ?? 'https://us.i.posthog.com');
  } else if (provider == 'mixpanel') {
    apiKey = apiKey.isNotEmpty ? apiKey : (dotenv.env['MIXPANEL_PROJECT_TOKEN'] ?? '');
    host = host.isNotEmpty ? host : (dotenv.env['MIXPANEL_API_HOST'] ?? '');
  }

  if (apiKey.isEmpty) return null;
  return AnalyticsProviderConfig(provider: provider, apiKey: apiKey, host: host);
}

typedef AnalyticsBuilder = Future<AnalyticsAdapter?> Function(AnalyticsProviderConfig config);

Future<AnalyticsAdapter?> _buildPostHogAdapter(AnalyticsProviderConfig config) async {
  return PostHogAnalyticsAdapter.init(
    apiKey: config.apiKey,
    host: config.host.isEmpty ? 'https://us.i.posthog.com' : config.host,
  );
}

Future<AnalyticsAdapter?> _buildMixpanelAdapter(AnalyticsProviderConfig config) async {
  return MixpanelAnalyticsAdapter.init(
    token: config.apiKey,
    serverUrl: config.host.isEmpty ? null : config.host,
  );
}

final Map<String, AnalyticsBuilder> _registry = <String, AnalyticsBuilder>{
  'posthog': _buildPostHogAdapter,
  'mixpanel': _buildMixpanelAdapter,
};
