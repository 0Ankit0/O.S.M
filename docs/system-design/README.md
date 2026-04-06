# Restaurant Order Management System

This documentation set describes a Django-first restaurant OMS. The application is implemented as a single Django web platform that serves both backend business logic and frontend HTML through server-rendered templates, with Tailwind CSS providing the shared UI system.

The source-of-truth stack is:

- Django for backend logic, routing, forms, sessions, and template rendering
- Tailwind CSS for the user-facing and admin-facing UI layers
- PostgreSQL as the canonical datastore
- Redis for caching, idempotency support, and short-lived coordination
- Celery for background workflows and scheduled jobs
- Local or S3-compatible object storage for uploaded and generated files
- Provider abstractions for payments, notifications, analytics, and maps

## Product Shape

The customer experience is a menu-first restaurant storefront with:

- restaurant landing page with direct order intent
- featured products near the top
- category-first menu browsing
- concise product cards with prices and fast add-to-cart behavior

The OMS extends that storefront with:

- authenticated customer accounts
- saved delivery addresses and serviceability checks
- owned cart and checkout
- order history and milestone tracking
- admin and staff operations
- analytics and reporting foundations

## Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Web application | Django | Handles routing, server-rendered templates, forms, sessions, auth, and domain orchestration |
| Frontend styling | Tailwind CSS | Shared design tokens, responsive layout primitives, utility-first styling in templates |
| Background jobs | Celery | Notifications, exports, retries, reconciliation, scheduled resets |
| Database | PostgreSQL | System of record for users, catalog, orders, deliveries, refunds, and reports |
| Cache / coordination | Redis | Caching, lightweight coordination, idempotency support, hot-path state |
| Object storage | Local or S3-compatible | Product images, proof-of-delivery evidence, generated reports and invoices |
| Analytics | Provider abstraction | PostHog, Mixpanel, and future adapters through one shared interface |
| Communications | Provider abstraction | Email-first notifications with future adapter support |

## Frontend Layout Contracts

The frontend is organized around two base templates:

- `templates/base_user.html` for storefront, account, cart, checkout, and order pages
- `templates/base_admin.html` for staff and admin dashboards, catalog operations, reporting, and configuration

Shared partials live under a common templates partials area and cover:

- header and footer
- sidebar navigation
- alerts and flash messages
- breadcrumbs
- page titles and contextual actions

Every page template extends one of the two base layouts. Full-page chrome should not be duplicated in leaf templates.

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

- Django as the single runtime for both frontend and backend
- Tailwind-powered server-rendered UI, not a separate SPA frontend
- Two intentional layout shells: customer-facing and admin-facing
- Domain-oriented Django apps for catalog, commerce, orders, delivery, notifications, and reporting
- PostgreSQL as canonical business data
- Redis and Celery as supporting infrastructure, not the source of truth

## Recommended Reading Order

1. [requirements-document.md](requirements/requirements-document.md)
2. [user-stories.md](requirements/user-stories.md)
3. [reference-site-analysis.md](requirements/reference-site-analysis.md)
4. [architecture-diagram.md](high-level-design/architecture-diagram.md)
5. [cloud-architecture.md](infrastructure/cloud-architecture.md)
6. [implementation-playbook.md](implementation/implementation-playbook.md)

## Documentation Note

Some older supporting documents may still describe legacy cloud-native or multi-client assumptions. When that conflicts with this overview, the Django monolith architecture and the updated implementation documents take precedence.
