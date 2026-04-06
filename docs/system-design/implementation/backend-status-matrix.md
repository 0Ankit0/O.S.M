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
