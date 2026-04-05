export interface AnalyticsProviderConfig {
  provider: string;
  apiKey: string;
  host?: string;
  options?: Record<string, unknown>;
}
