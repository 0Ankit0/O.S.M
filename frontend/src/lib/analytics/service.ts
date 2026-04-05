/**
 * AnalyticsService — the public API consumed by the rest of the frontend.
 *
 * This is the Context in the Strategy pattern.  It holds a reference to an
 * AnalyticsAdapter and delegates every operation to it.  When analytics are
 * disabled (adapter is null) all methods silently no-op.
 *
 * Usage
 * -----
 *   import { analytics } from '@/lib/analytics';
 *   analytics.capture('my_event', { foo: 'bar' });
 *
 *   // Or use the hook for React components:
 *   const { capture, isEnabled } = useAnalytics();
 */
import type { AnalyticsAdapter } from './interface';
import type { AnalyticsProviderConfig } from './base';

export class AnalyticsService {
  private adapter: AnalyticsAdapter | null;

  constructor(adapter: AnalyticsAdapter | null) {
    this.adapter = adapter;
  }

  get enabled(): boolean {
    return this.adapter !== null;
  }

  /** Replace the active adapter at runtime (useful for testing). */
  setAdapter(adapter: AnalyticsAdapter | null): void {
    this.adapter = adapter;
  }

  // ------------------------------------------------------------------
  // Sending operations
  // ------------------------------------------------------------------

  capture(event: string, properties?: Record<string, unknown>): void {
    try { this.adapter?.capture(event, properties); } catch { /* silent */ }
  }

  identify(userId: string, properties?: Record<string, unknown>): void {
    try { this.adapter?.identify(userId, properties); } catch { /* silent */ }
  }

  reset(): void {
    try { this.adapter?.reset(); } catch { /* silent */ }
  }

  page(name?: string, properties?: Record<string, unknown>): void {
    try { this.adapter?.page(name, properties); } catch { /* silent */ }
  }

  group(groupType: string, groupKey: string, properties?: Record<string, unknown>): void {
    try { this.adapter?.group(groupType, groupKey, properties); } catch { /* silent */ }
  }

  // ------------------------------------------------------------------
  // Retrieving operations
  // ------------------------------------------------------------------

  getFeatureFlag(flag: string): boolean | string | undefined {
    try { return this.adapter?.getFeatureFlag(flag); } catch { return undefined; }
  }

  isFeatureFlagEnabled(flag: string): boolean {
    try { return this.adapter?.isFeatureFlagEnabled(flag) ?? false; } catch { return false; }
  }

  reloadFeatureFlags(): void {
    try { this.adapter?.reloadFeatureFlags(); } catch { /* silent */ }
  }
}

// ------------------------------------------------------------------
// Singleton factory
// ------------------------------------------------------------------

type AnalyticsBuilder = (config: AnalyticsProviderConfig) => AnalyticsAdapter | null;

function buildPostHogAdapter(config: AnalyticsProviderConfig): AnalyticsAdapter | null {
  if (!config.apiKey) return null;
  const { PostHogAdapter } = require('./adapters/posthog') as typeof import('./adapters/posthog');
  return new PostHogAdapter(config.apiKey, config.host ?? 'https://us.i.posthog.com');
}

function buildMixpanelAdapter(config: AnalyticsProviderConfig): AnalyticsAdapter | null {
  if (!config.apiKey) return null;
  const { MixpanelAdapter } = require('./adapters/mixpanel') as typeof import('./adapters/mixpanel');
  return new MixpanelAdapter(config.apiKey, config.host);
}

const REGISTRY: Record<string, AnalyticsBuilder> = {
  posthog: buildPostHogAdapter,
  mixpanel: buildMixpanelAdapter,
};

function resolveConfig(): AnalyticsProviderConfig | null {
  const enabled = process.env.NEXT_PUBLIC_ANALYTICS_ENABLED === 'true';
  if (!enabled) return null;
  const provider = (process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER ?? 'posthog').toLowerCase();
  let apiKey = process.env.NEXT_PUBLIC_ANALYTICS_API_KEY ?? '';
  let host = process.env.NEXT_PUBLIC_ANALYTICS_HOST ?? '';

  if (provider === 'posthog') {
    apiKey = apiKey || process.env.NEXT_PUBLIC_POSTHOG_KEY || '';
    host = host || process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com';
  } else if (provider === 'mixpanel') {
    apiKey =
      apiKey ||
      process.env.NEXT_PUBLIC_MIXPANEL_PROJECT_TOKEN ||
      process.env.NEXT_PUBLIC_POSTHOG_KEY ||
      '';
    host =
      host ||
      process.env.NEXT_PUBLIC_MIXPANEL_HOST ||
      process.env.NEXT_PUBLIC_MIXPANEL_API_HOST ||
      '';
  }

  return { provider, apiKey, host };
}

function buildService(): AnalyticsService {
  // Only initialise in the browser — posthog-js is browser-only
  if (typeof window === 'undefined') {
    return new AnalyticsService(null);
  }

  const config = resolveConfig();
  if (!config) {
    return new AnalyticsService(null);
  }
  const builder = REGISTRY[config.provider];
  if (!builder) {
    console.warn(`Unknown analytics provider "${config.provider}". Analytics disabled.`);
    return new AnalyticsService(null);
  }
  return new AnalyticsService(builder(config));
}

/** Module-level singleton — initialised lazily on first import. */
export const analytics = buildService();
