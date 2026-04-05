# Backend Status Matrix

This matrix reflects the FastAPI backend that exists in this repository today against the updated restaurant OMS requirements. The runtime is a single FastAPI application with OMS domain modules, PostgreSQL as the canonical datastore, Redis for idempotency and hot-path support, Celery for background workflows, and provider abstractions for payments, communications, analytics, and storage.

Status labels:

- `core`: implemented and already part of the working backbone
- `in progress`: main flow works, but edge cases or surrounding tooling still need more depth
- `planned`: documented next step, not yet implemented in this codebase
- `removed`: previously planned; explicitly out of scope for this restaurant system

| Area | Capability | Status |
|---|---|---|
| Auth | JWT-based auth, session refresh, token tracking, user profile endpoints | `core` |
| Auth | OTP / MFA support and account security controls | `core` |
| Catalog | Category CRUD (unlimited depth hierarchy) | `core` |
| Catalog | Product CRUD with variants, featured flags, tags, pricing | `core` |
| Catalog | Product **published** toggle (inline from list) | `in progress` |
| Catalog | Product **daily availability** toggle (per-day on/off) | `planned` |
| Catalog | Customer catalog browsing — published + available today only | `in progress` |
| Customer | Address CRUD with serviceability checks and default address handling | `core` |
| Customer | Address lock after order initiation | `in progress` |
| Cart | Add, update, remove, and view cart items | `core` |
| Cart | Coupon-aware cart totals and price snapshotting | `core` |
| Cart | Zone-based delivery fee applied at cart/checkout | `in progress` |
| Checkout | Checkout endpoint with `Idempotency-Key` enforcement | `core` |
| Checkout | Address lock on checkout confirmation | `in progress` |
| Orders | Order creation, listing, detail view, cancellation | `core` |
| Orders | Milestone recording and guarded state transitions | `core` |
| Orders | Google Maps Distance Matrix ETA on order detail | `planned` |
| Delivery | Delivery assignment creation during checkout bootstrap | `core` |
| Delivery | Delivery status updates with **GPS lat/lon capture** per update | `planned` |
| Delivery | Reassignment and failed-delivery handling | `core` |
| Delivery | Proof-of-delivery: signature **or** photo required before `Delivered` | `in progress` |
| Delivery | Delivery zone management with per-zone fee | `core` |
| Refunds | Admin refund request dashboard (approve / deny) | `planned` |
| Refunds | Full-order Stripe refund on admin approval (no partial, no automatic) | `planned` |
| Reviews | Customer order review and rating (1–5, per delivered order) | `planned` |
| Reviews | Admin review moderation (hide/flag) | `planned` |
| Reviews | Average rating and review count on storefront | `planned` |
| Notifications | Email-only transactional notifications | `in progress` |
| Notifications | Admin custom message broadcast (compose + segment + schedule) | `planned` |
| Notifications | SMS channel present but disabled (`SMS_ENABLED=false`) | `planned` |
| Notifications | Notification templates with i18n (de/en) support | `planned` |
| Payments | Stripe integration for credit/debit cards and digital wallets | `in progress` |
| Payments | Payment reconciliation reports | `in progress` |
| i18n | German (de) and English (en) language toggle in web and mobile | `planned` |
| i18n | EUR locale formatting (currency, dates, numbers) per selected language | `planned` |
| Reports | Weekly auto-generated summary report (Mon–Sun) | `planned` |
| Reports | Excel (XLSX), CSV, PDF export for reports | `planned` |
| Reports | 80 mm thermal receipt print layout | `planned` |
| Reports | PDF invoice generation and print | `planned` |
| Analytics | Provider-agnostic analytics base across backend, web, and mobile | `core` |
| Analytics | OMS event taxonomy for catalog, cart, checkout, order, delivery, refund, admin | `core` |
| Admin / Ops | Overview metrics, delivery-zone list | `core` |
| Admin / Ops | Product admin updates, publish/availability toggles | `in progress` |
| Audit | Audit log for all admin and staff actions | `in progress` |
| Inventory | Stock tracking, reservations, low-stock alerts | `removed` |
| Fulfillment | Warehouse pick-pack-ship workflow | `removed` |
| Returns | Return pickup by delivery staff | `removed` |
| Returns | Warehouse inspection and partial accept | `removed` |
| Payments | Khalti gateway | `removed` |
| Payments | Partial refunds | `removed` |

## Verified OMS Flows

The backend currently has integration coverage for:

- category and product setup
- address creation
- cart add and coupon application
- checkout with idempotent replay
- order listing and cancellation
- delivery status updates
- proof-of-delivery submission

## Current Gaps Worth Prioritising

1. GPS coordinate capture on every delivery status update
2. Admin refund approval dashboard (no automatic refund)
3. Daily product availability toggle and auto-reset via Celery
4. Product published toggle inline from the admin product list
5. i18n: German/English language toggle with EUR locale formatting
6. Google Maps ETA integration on order tracking
7. Weekly report generation (Celery scheduled task)
8. Excel (XLSX) + PDF export and 80 mm thermal receipt printing
9. Customer order review and rating module
10. Admin custom notification broadcast
11. Address lock enforcement after checkout confirmation
