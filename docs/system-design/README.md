# Restaurant Order Management System

This documentation set describes the restaurant-focused OMS implemented in this repository. The live product direction is a Sushi & More style storefront backed by a full internal operations platform for catalog management, checkout, fulfillment, delivery, returns, notifications, and analytics.

The source-of-truth stack is:

- FastAPI backend
- Next.js web application
- Flutter mobile application
- PostgreSQL as the canonical datastore
- Redis for idempotency, caching, and short-lived coordination
- Celery for background workflows
- Local or S3-compatible object storage for artifacts
- Provider abstractions for payments, notifications, analytics, and maps

## Product Shape

The customer experience follows the reference storefront in [reference-site-analysis.md](requirements/reference-site-analysis.md):

- restaurant landing page with direct order intent
- featured products near the top
- category-first menu browsing
- concise product cards with prices and fast add-to-cart behavior

The OMS extends that storefront with:

- authenticated customer accounts
- saved delivery addresses and serviceability checks
- owned cart and checkout
- order history and milestone tracking
- admin catalog workflows
- fulfillment, delivery, and return operations
- analytics and reporting foundations

## Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Backend API | FastAPI | Modular OMS backend with domain-oriented routers, services, schemas, and models |
| Web | Next.js | Customer storefront and admin/ops dashboards |
| Mobile | Flutter | Customer-first mobile flows using the same OMS contracts |
| Database | PostgreSQL | System of record for users, catalog, orders, fulfillment, deliveries, and returns |
| Cache / coordination | Redis | Idempotency keys, hot-path caching, reservation timing, lightweight coordination |
| Background jobs | Celery | Notifications, reservation expiry, exports, retries, reconciliation |
| Object storage | Local or S3-compatible | Product images, proof-of-delivery evidence, generated reports |
| Analytics | Provider abstraction | PostHog, Mixpanel, and future adapters through one shared interface |
| Communications | Provider abstraction | Email, SMS, push, and in-app notifications |

## Documentation Structure

```text
docs/system-design/
├── requirements/
│   ├── requirements-document.md
│   ├── user-stories.md
│   └── reference-site-analysis.md
├── analysis/
├── high-level-design/
│   └── architecture-diagram.md
├── detailed-design/
├── infrastructure/
│   └── cloud-architecture.md
├── edge-cases/
└── implementation/
    ├── analytics-architecture.md
    ├── code-guidelines.md
    └── implementation-playbook.md
```

## Key Implementation Themes

- Menu-first restaurant storefront, not a generic marketplace
- FastAPI as the single backend runtime
- OMS domain modules for catalog, commerce, orders, fulfillment, delivery, returns, and reporting
- Customer-first mobile in the current implementation wave
- Web-first staff and admin operations
- Analytics designed as a switchable provider layer instead of a vendor lock-in point

## Recommended Reading Order

1. [requirements-document.md](requirements/requirements-document.md)
2. [user-stories.md](requirements/user-stories.md)
3. [reference-site-analysis.md](requirements/reference-site-analysis.md)
4. [architecture-diagram.md](high-level-design/architecture-diagram.md)
5. [cloud-architecture.md](infrastructure/cloud-architecture.md)
6. [analytics-architecture.md](implementation/analytics-architecture.md)

## Documentation Note

Some older detailed analysis documents may still reference AWS-native terms from the original planning phase. When that conflicts with the codebase, the implementation in this repository and the updated architecture documents take precedence.
