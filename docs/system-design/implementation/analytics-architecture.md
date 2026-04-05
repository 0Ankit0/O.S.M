# Analytics Architecture

## Overview

The OMS analytics layer is provider-agnostic across backend, web, and mobile. Product code talks to one analytics service contract, while provider-specific SDK logic stays isolated inside adapters.

PostHog and Mixpanel are first-class adapters today, and new providers can be added through a registry entry instead of changing feature code.

## Design Goals

- Keep OMS features decoupled from vendor SDKs.
- Allow provider switching by configuration.
- Keep analytics disabled mode safe and silent.
- Use one mental model across FastAPI, Next.js, and Flutter.
- Keep feature-flag reads behind the same contract where supported.

## Common Contract

Every analytics implementation supports the same core operations:

- `capture`
- `identify`
- `group`
- `page` or `screen`
- feature-flag evaluation
- `flush`
- `shutdown`

Feature code should only depend on these operations.

## Provider Selection

### Generic config

Preferred environment variables:

- `ANALYTICS_ENABLED`
- `ANALYTICS_PROVIDER`
- `ANALYTICS_API_KEY`
- `ANALYTICS_HOST`

Frontend equivalents:

- `NEXT_PUBLIC_ANALYTICS_ENABLED`
- `NEXT_PUBLIC_ANALYTICS_PROVIDER`
- `NEXT_PUBLIC_ANALYTICS_API_KEY`
- `NEXT_PUBLIC_ANALYTICS_HOST`

### Compatibility fallbacks

Provider-specific variables remain supported:

- PostHog: `POSTHOG_API_KEY`, `POSTHOG_HOST`
- Mixpanel: `MIXPANEL_PROJECT_TOKEN`, `MIXPANEL_API_HOST`

## Adding A New Provider

### Backend

1. Add `backend/src/apps/analytics/adapters/<provider>_adapter.py`.
2. Implement `AnalyticsProvider`.
3. Register the builder in `backend/src/apps/analytics/factory.py`.

### Frontend

1. Add `frontend/src/lib/analytics/adapters/<provider>.ts`.
2. Implement `AnalyticsAdapter`.
3. Register the builder in `frontend/src/lib/analytics/service.ts`.

### Mobile

1. Add `mobile/lib/core/analytics/adapters/<provider>_adapter.dart`.
2. Implement `AnalyticsAdapter`.
3. Register the builder in `mobile/lib/core/analytics/analytics_provider.dart`.

## OMS Event Naming

Use business-level event names instead of provider-centric names.

Recommended namespaces:

- `catalog.*`
- `cart.*`
- `checkout.*`
- `order.*`
- `fulfillment.*`
- `delivery.*`
- `returns.*`
- `admin.*`

Examples:

- `catalog.product_viewed`
- `catalog.collection_viewed`
- `cart.item_added`
- `checkout.started`
- `order.created`
- `delivery.status_updated`
- `returns.requested`

### Restaurant OMS baseline events

The restaurant implementation should treat these as the default high-value event set:

- `catalog.product_viewed`
- `cart.item_added`
- `checkout.started`
- `order.created`
- `order.cancelled`
- `delivery.status_updated`
- `returns.requested`
- `admin.product_updated`

Suggested payload fields:

- `product_id`
- `product_title`
- `category_id`
- `order_id`
- `order_number`
- `delivery_assignment_id`
- `return_id`
- `actor_role`

## Operational Notes

- Unknown providers disable analytics safely instead of breaking app startup.
- Runtime provider swaps are supported in services and tests.
- Feature-flag methods must return safe defaults when unsupported.
- Adapters own SDK initialization and shutdown details; feature code must not.
