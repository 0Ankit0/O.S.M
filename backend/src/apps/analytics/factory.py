"""Analytics factory — registry-based provider construction."""
import logging
from collections.abc import Callable

from src.apps.analytics.base import AnalyticsProviderConfig
from src.apps.core.config import settings
from src.apps.analytics.interface import AnalyticsProvider
from src.apps.analytics.service import AnalyticsService

logger = logging.getLogger(__name__)


def _resolve_config() -> AnalyticsProviderConfig | None:
    if not settings.ANALYTICS_ENABLED:
        return None
    provider_name = settings.ANALYTICS_PROVIDER.lower().strip()
    api_key = settings.ANALYTICS_API_KEY or ""
    host = settings.ANALYTICS_HOST or ""

    if provider_name == "posthog":
        api_key = api_key or settings.POSTHOG_API_KEY
        host = host or settings.POSTHOG_HOST
    elif provider_name == "mixpanel":
        api_key = api_key or settings.MIXPANEL_PROJECT_TOKEN
        host = host or settings.MIXPANEL_API_HOST

    return AnalyticsProviderConfig(
        provider=provider_name,
        api_key=api_key,
        host=host,
        extra={"mixpanel_api_secret": settings.MIXPANEL_API_SECRET},
    )


def _build_posthog(config: AnalyticsProviderConfig) -> AnalyticsProvider | None:
    if not config.api_key:
        logger.warning("Analytics provider 'posthog' selected but no api key is configured.")
        return None
    from src.apps.analytics.adapters.posthog_adapter import PostHogAdapter
    return PostHogAdapter(api_key=config.api_key, host=config.host or settings.POSTHOG_HOST)


def _build_mixpanel(config: AnalyticsProviderConfig) -> AnalyticsProvider | None:
    if not config.api_key:
        logger.warning("Analytics provider 'mixpanel' selected but no project token is configured.")
        return None
    from src.apps.analytics.adapters.mixpanel_adapter import MixpanelAdapter
    return MixpanelAdapter(
        project_token=config.api_key,
        host=config.host or settings.MIXPANEL_API_HOST,
    )


_REGISTRY: dict[str, Callable[[AnalyticsProviderConfig], AnalyticsProvider | None]] = {
    "posthog": _build_posthog,
    "mixpanel": _build_mixpanel,
}


def _build_provider() -> AnalyticsProvider | None:
    """Instantiate and return the configured analytics provider, or None."""
    config = _resolve_config()
    if config is None:
        return None
    builder = _REGISTRY.get(config.provider)
    if builder is None:
        logger.warning(
            "Unknown ANALYTICS_PROVIDER=%r — analytics disabled. Registered providers: %s",
            config.provider,
            ", ".join(sorted(_REGISTRY.keys())),
        )
        return None
    return builder(config)


def build_analytics_service() -> AnalyticsService:
    """Return an AnalyticsService wired to the configured provider."""
    provider = _build_provider()
    return AnalyticsService(provider)
