# Verified Workflows

This document records the local setup and application workflows that were exercised and verified against the current repository state.

## 1. Local startup workflow

1. Start PostgreSQL locally and ensure it accepts `postgres/postgres` on `localhost:5432`.
2. Confirm `.env` uses the Postgres JSON connection string in `DB_CONNECTION`.
3. Run:

   ```bash
   pipenv install --dev
   npm install
   pipenv run python manage.py migrate
   pipenv run python manage.py check
   pipenv run python manage.py runserver
   ```

4. Open `http://127.0.0.1:8000/`.

## 2. Authentication workflow

Validated:

- Login page renders and authenticates with email/password.
- Signup succeeds with the custom IAM user model.
- Password reset request page renders and accepts an email.
- Social login buttons remain hidden when OAuth keys are placeholders.

Demo credentials used during validation:

- Customer: `customer@example.com` / `password123`
- Admin: `admin@example.com` / `password123`

## 3. Customer workflow

Validated customer paths:

- Home page: `/`
- Catalog: `/catalog/`
- Product detail pages from catalog links
- Orders hub: `/orders/`
- Cart and checkout: `/orders/cart/`, `/orders/checkout/`
- Order history and order detail pages
- Account/settings: `/settings/`, `/settings/security/`
- Payments dashboard and transaction detail pages: `/dashboard/payments/`

Behavior confirmed during validation:

- Navigation now routes authenticated customers to working order history and settings pages.
- The orders landing page and account landing page now act as usable hubs instead of placeholders.
- Checkout only offers Cash on Delivery in the local environment because online gateways are not configured.
- Existing seeded payment transactions remain visible, but provider-backed actions are hidden when the gateway is not enabled.
- The security page now supports signing out other active sessions.

## 4. Staff workflow

Validated staff paths:

- Admin dashboard: `/dashboard/`
- Payments overview and transactions: `/dashboard/payments/`, `/dashboard/payments/transactions/`
- Delivery dashboard: `/dashboard/delivery/`
- Reporting dashboard: `/dashboard/reporting/`
- Catalog menu, category, and product detail: `/catalog/`, `/catalog/category/<slug>/`, `/catalog/products/<id_or_slug>/`

Behavior confirmed during validation:

- The operations dashboard now lists only memberships for active organizations.
- The staff payments overview and transaction list render cleanly even when online providers are disabled.
- Catalog menu, category, and product-detail pages render successfully in a staff session.
- Staff navigation exposes delivery and reporting pages.
- Customer navigation no longer exposes the reporting page that produced a 403.

## 5. Payment workflow notes

Current local behavior:

- `STRIPE_ENABLED` is derived from the active Stripe mode and real keys.
- The payment gateway factory now only exposes gateways that are actually enabled in settings.
- The payments index no longer shows a create-session CTA when no provider is configured.
- Payment detail pages hide refresh/refund actions when the underlying provider is unavailable.

If you want online payments locally, set real provider credentials in `.env` and re-run `pipenv run python manage.py check`.

## 6. Content workflow

Validated content paths:

- Documents list and upload: `/documents/`, `/documents/upload/`
- Product create/list: `/products/create/`, `/products/`
- Product purchase handoff: `/finances/payment-methods/?product_id=<hashid>`

Behavior confirmed during validation:

- Document upload now succeeds even when the user omits a title because the server derives one from the uploaded filename.
- Document delete works with hashid IDs and submits through a CSRF-protected POST form.
- Content document and product screens now render their own namespaced templates instead of shadowed templates from other apps.
- Product creation now lands on a working list page with a real `Buy Now` action into the payment summary flow.

## 7. Organization workflow

Validated organization paths:

- Tenant list and create: `/tenants/`, `/tenants/create/`
- Tenant detail and invite: `/tenants/<hashid>/`, `/tenants/<hashid>/invite/`
- Tenant switching and member/tenant removal actions from the tenant detail page

Behavior confirmed during validation:

- Creating an organization now persists a valid tenant type and owner membership.
- Inviting a member creates a pending membership instead of calling a missing invitation model.
- Owner/admin controls are visible again because template role checks now match the stored uppercase role values.
- Tenant removal and organization deletion actions now post to implemented endpoints.
- Soft-deleted tenants and memberships no longer appear in active lists.

## 8. Notifications workflow

Validated notification paths:

- Notification center: `/notifications/`
- Per-notification read action and bulk read action from the list page

Behavior confirmed during validation:

- Individual notification reads now submit correctly with CSRF protection.
- `Mark all as read` updates unread notifications through `read_at` and leaves no unread action buttons behind.
- Notification routes now accept the repository's hashid-based IDs.

## 9. Subscription-plan workflow

Validated finance paths:

- Add plan: `/finances/plans/add/`
- Subscription management: `/finances/subscription/`
- Plan selection handoff: `/finances/payment-methods/?plan=<price_id>`

Behavior confirmed during validation:

- The local environment can create plans without real Stripe credentials through an offline dj-stripe-compatible fallback.
- Newly created plans appear immediately on the subscription page.
- Selecting a plan opens a working payment summary page even when online gateways are disabled.

## 10. Known local constraints

- The checked-in local `.env` leaves Stripe keys as placeholders and sets `KHALTI_ENABLED=False`.
- The settings page intentionally does not expose account deletion in the local demo UI.
- The application still contains optional integrations that require external services beyond the scope of this validation pass.