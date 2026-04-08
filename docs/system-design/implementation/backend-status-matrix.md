# Backend Status Matrix

This matrix reflects the documented Django target for the restaurant OMS. Django is the single runtime for storefront, customer account flows, and staff/admin operations. PostgreSQL is the canonical datastore, Redis supports caching and idempotency, Celery runs background workflows, and Tailwind powers the server-rendered UI.

Status labels:

- `core`: part of the documented platform backbone
- `in progress`: main flow is defined but still needs implementation depth
- `planned`: documented next step, not yet delivered
- `removed`: explicitly out of scope for this restaurant system

| Area | Capability | Status |
|---|---|---|
| Auth | Django session auth, login/logout, password reset | `core` |
| Auth | Role-based access via Django groups and permissions | `core` |
| Auth | Staff/admin route protection and permission-aware navigation | `core` |
| Frontend | `base_user.html` for storefront and customer pages | `core` |
| Frontend | `base_admin.html` for staff/admin pages | `core` |
| Frontend | Shared partials for header, footer, sidebar, alerts, breadcrumbs | `core` |
| Frontend | Tailwind tokenized design system across both layouts | `in progress` |
| Catalog | Category CRUD and merchandising flows | `core` |
| Catalog | Product CRUD with variants, featured flags, tags, pricing | `core` |
| Catalog | Product published toggle from admin list | `in progress` |
| Catalog | Product daily availability toggle | `planned` |
| Customer | Address CRUD with serviceability checks and defaults | `core` |
| Cart | Add, update, remove, and view cart items | `core` |
| Cart | Async cart refresh endpoints for progressive enhancement | `in progress` |
| Checkout | Server-rendered checkout with payment initiation | `core` |
| Orders | Order creation, listing, detail view, cancellation | `core` |
| Orders | Timeline and status tracking | `core` |
| Delivery | Delivery status updates with GPS metadata | `planned` |
| Delivery | Proof-of-delivery upload before `Delivered` | `in progress` |
| Refunds | Admin refund review flow in admin layout | `planned` |
| Notifications | Email-only transactional notifications | `in progress` |
| Notifications | Admin custom message broadcast | `planned` |
| Notifications | Editable notification templates | `planned` |
| Payments | Stripe integration | `in progress` |
| Payments | Reconciliation reports | `planned` |
| Reporting | Dashboard metrics and exports | `planned` |
| Reporting | PDF invoice and 80 mm receipt generation | `planned` |
| i18n | German and English language support in templates and emails | `planned` |
| Analytics | Provider-agnostic business event taxonomy | `core` |
| Inventory | Stock tracking and reservations | `removed` |
| Fulfillment | Warehouse pick-pack workflows | `removed` |
| Returns | Warehouse return inspection workflow | `removed` |
| Mobile | Separate mobile app as current product surface | `removed` |

## Current Gaps Worth Prioritising

1. Finalize the Tailwind design tokens and responsive rules for both layouts.
2. Document child template conventions for storefront, account, and dashboard pages.
3. Build admin refund review and notification management inside the custom admin shell.
4. Add delivery GPS capture, ETA refresh, and POD enforcement details.
5. Complete i18n coverage for templates, emails, and locale-aware formatting.

## Module Status (Implementation Snapshot)

| Module | Web Namespace | API Namespace | Status | Notes |
|---|---|---|---|---|
| Core | `core` | n/a | `core` | Home + dashboard shell routing in place. |
| IAM | `iam` | `iam_api` | `core` | Auth, profile, and social auth API surface. |
| Accounts | `accounts` | `accounts_api` | `core` | Customer profile, address, and notification preferences. |
| Catalog | `catalog` | `catalog_api` | `core` | Public browse/list/detail for categories and products. |
| Orders | `orders` | `orders_api` | `core` | Cart, checkout, and order history/detail flows. |
| Payments | `payments` | `payments_api` | `in progress` | Payment intent, status sync, refund requests, webhooks. |
| Delivery | `delivery` | `delivery_api` | `in progress` | Serviceability, assignment updates, timeline endpoint. |
| Reporting | `reporting` | `reporting_api` | `in progress` | Export job request/status/download workflows. |
| Finances | `finances` | `finances_api` | `core` | Subscriptions, payment methods, admin refund touchpoints. |
| Notifications | `notifications` | `notifications_api` | `core` | Read/list + unread count + bulk read action. |
| Content | `content` | `content_api` | `core` | CMS sync webhook, content/items/documents/pages APIs. |
| Integrations | `integrations` | `integrations_api` | `in progress` | OpenAI idea generation integration endpoint. |
| Multitenancy | `multitenancy` | `multitenancy_api` | `core` | Tenant, membership, invitation, and tenant switching. |

## Endpoint Inventory (Key Integration Routes)

- `catalog_api`
  - `GET /api/catalog/categories/`
  - `GET /api/catalog/products/`
  - `GET /api/catalog/products/{id_or_slug}/`
- `orders_api`
  - `GET /api/orders/cart/`
  - `POST /api/orders/cart/items/`
  - `PATCH|DELETE /api/orders/cart/items/{item_id}/`
  - `POST /api/orders/checkout/`
  - `GET /api/orders/orders/`, `GET /api/orders/orders/{id}/`
- `payments_api`
  - `POST /api/payments/intents/`
  - `GET /api/payments/{payment_id}/status/`
  - `POST /api/payments/refunds/`
  - `POST /api/payments/webhooks/{provider}/`
- `delivery_api`
  - `GET /api/delivery/serviceability/`
  - `PATCH /api/delivery/assignments/{assignment_id}/status/`
  - `GET /api/delivery/orders/{order_id}/timeline/`
- `reporting_api`
  - `POST /api/reporting/exports/`
  - `GET /api/reporting/exports/{job_id}/`
  - `GET /api/reporting/exports/{job_id}/download/`

## Edge-case Coverage Snapshot

| Edge Case | Status | Implementation Notes |
|---|---|---|
| Checkout idempotency replay | `core` | Existing idempotency key contract and tests in orders/payments modules. |
| Gateway checkout without callback URL | `core` | Checkout API now returns `400` unless `return_url` is provided with gateway input. |
| Duplicate payment session creation for same order | `core` | Payment intent creation now returns `409` when an order already has `payment_record`. |
| Delivery timeline access by non-owner | `core` | Timeline endpoint filters by authenticated order owner unless staff. |
| Dashboard export visibility | `core` | Reporting API uses staff permission gate and owner/superuser filtering. |
