# Implementation Playbook

## Overview

This playbook tracks how the restaurant OMS is being delivered in the actual monorepo. The implementation target is FastAPI + Next.js + Flutter, with PostgreSQL, Redis, Celery, and provider abstractions. It reflects the updated restaurant-specific requirements: food delivery and ordering for a German restaurant, no inventory, no warehouse, no reservations, no Khalti, Stripe-only payments, admin-gated refunds, i18n (de/en), and Google Maps ETA.

## Delivery Tracks

### Track 1. Foundation and doc realignment ✅

Goal:
- Align architecture docs with the real stack
- Introduce OMS constants, schemas, routers, models, and shared conventions
- Establish provider-agnostic analytics

Outcome:
- OMS backend module exists
- Analytics abstraction exists across backend, web, and mobile
- Architecture and core requirement docs updated to describe the FastAPI restaurant OMS
- Requirements and user stories rewritten to reflect Germany food-delivery context

---

### Track 2. Customer commerce ✅ (mostly complete)

Goal:
- Menu-first storefront (published products only)
- Product browsing, category filtering, cart, checkout, addresses, order history

Current outcome:
- Customer web shop, cart, orders, dashboard, and profile address book exist
- Customer mobile shop, cart, orders, and address management exist
- Checkout, cancellation, and address management exist in the backend
- Home page shows restaurant details and full menu; login required only for cart/order actions

---

### Track 3. Operations workflows (in progress)

Goal:
- Delivery assignment and milestone management with GPS location capture
- POD capture (signature or photo) required before `Delivered`
- Failed delivery handling
- Admin-gated refund approval (no automatic refunds)
- Zone-based delivery fee at checkout

Current outcome:
- Delivery status, reassignment, failure, and POD endpoints exist
- Admin operations pages exist for menu, deliveries, and overview metrics
- Zone management endpoints exist

Remaining work:
- Add lat/lon capture to every delivery status update endpoint
- Require POD before `Delivered` transition in state machine
- Build admin refund approval dashboard (approve/deny; no partial, no automatic)
- Enforce address lock after checkout confirmation
- Apply zone delivery fee automatically at checkout

---

### Track 4. Catalog management improvements (in progress)

Goal:
- Inline published toggle from product list page
- Daily availability toggle per product
- Category hierarchy without depth limit
- Search returns only published + available-today products

Remaining work:
- Add `is_available_today` field to product model with Celery daily reset job
- Expose bulk-toggle endpoint for published and daily availability
- Update storefront filtering to respect both `is_published` and `is_available_today`
- Update category backend to remove 3-level depth constraint

---

### Track 5. i18n — German and English

Goal:
- Language toggle (de/en) in web, mobile, and email templates
- EUR locale formatting per selected language
- All customer-facing and admin strings translated

Implementation approach:
- Web (Next.js): `next-intl` or `react-i18next` with `/messages/de.json` and `/messages/en.json`
- Mobile (Flutter): `flutter_localizations` + ARB files for de and en
- Email templates: separate de/en variants per event type in the notification template table
- Language preference persisted on the user model (`preferred_language` field)

---

### Track 6. Reviews and ratings

Goal:
- Customer can submit a 1–5 star review per delivered order
- Admin can moderate reviews
- Average rating shown on storefront

Implementation approach:
- New `OrderReview` model: `order_id`, `customer_id`, `rating`, `comment`, `photo_url`, `created_at`, `is_hidden`
- Review submission endpoint available only for `Delivered` orders (one per order, editable within 48 h)
- Admin moderation endpoint to hide/flag reviews
- Storefront home page aggregates average rating from non-hidden reviews

---

### Track 7. Reporting and printing

Goal:
- Weekly auto-generated report (Mon–Sun)
- Excel (XLSX), CSV, PDF export
- 80 mm thermal receipt printing
- PDF invoice generation

Implementation approach:
- Celery beat task runs each Monday at 00:01 generating the weekly report and storing to object storage
- XLSX export: `openpyxl` library
- PDF generation: `weasyprint` or `reportlab`
- Thermal receipt: 80 mm-width PDF at 72 dpi rendered client-side or via backend endpoint
- "Print Receipt" and "Print Invoice" buttons on the admin order detail page

---

### Track 8. Google Maps ETA

Goal:
- Show estimated delivery time on order tracking page and in emails

Implementation approach:
- Backend calls Google Maps Distance Matrix API (async via Celery or inline) on order confirmation and on each delivery status update
- ETA stored on the order record and refreshed on status change
- `GOOGLE_MAPS_API_KEY` configured via environment
- ETA displayed on the customer order detail page and included in status change emails

---

### Track 9. Custom notification broadcast

Goal:
- Admin can compose and send a custom email to customers or a segment

Implementation approach:
- New `CustomNotification` model: `subject`, `body`, `sender_id`, `scheduled_at`, `sent_at`, `recipient_filter`
- Admin dashboard: compose form with recipient filter (all, by zone, by last order date)
- Celery task sends emails via the existing email provider adapter
- Audit record created with sender, timestamp, and recipient count

---

## Near-Term Roadmap

### Backend

1. Add `is_available_today` to product model + Celery daily reset job
2. Add GPS lat/lon to delivery status update endpoint
3. Build admin refund approval API (approve/deny; full-order Stripe refund on approval)
4. Add `preferred_language` to user model
5. Integrate Google Maps Distance Matrix for ETA
6. Create `OrderReview` model and endpoints
7. Build weekly report Celery task with XLSX/PDF output
8. Add `CustomNotification` model and broadcast endpoint
9. Remove or disable Khalti payment adapter references
10. Enforce address-lock logic in order state machine

### Web (Next.js)

1. Add inline published + daily availability toggles to admin product list page
2. Build admin refund dashboard (pending → approve/deny)
3. Add i18n infrastructure (de/en toggle, persisted per user)
4. Add review submission form on order detail page (post-delivery)
5. Show Google Maps ETA on customer order tracking page
6. Add "Print Receipt" (80 mm) and "Print Invoice" (PDF) buttons on admin order detail
7. Build weekly reports page with XLSX/CSV/PDF download
8. Build admin custom notification broadcast page

### Mobile (Flutter)

1. Add GPS capture to delivery status update flow
2. Block `Delivered` transition until POD (signature or photo) is provided
3. Add i18n: de/en language toggle
4. Add order review form on delivered order detail page

## Working Principles

- Prefer vertical slices that are shippable end-to-end.
- Keep docs updated when behaviour changes materially.
- Treat PostgreSQL as canonical business data.
- Use Redis for idempotency and hot-path coordination, not as the source of truth.
- Keep analytics, notifications, payments, and storage behind provider interfaces.
- Preserve the menu-first storefront behaviour while extending it into a full OMS.
- No inventory tracking — product availability is a manual daily toggle, not a stock counter.
- All refunds are admin-approved; the system never initiates a refund automatically.

## Cutover Readiness Checklist

### Product readiness

- [ ] Customer can browse the published, available-today menu; add items to cart; and place orders
- [ ] Customer can view orders, milestones, Google Maps ETA, and POD
- [ ] Customer can submit a refund request and track its status
- [ ] Customer can leave a review for a delivered order
- [ ] Customer can select German or English language
- [ ] Admin can toggle product published state from the product list page
- [ ] Admin can toggle daily availability per product
- [ ] Admin can approve or deny refund requests
- [ ] Admin can send custom notification broadcasts
- [ ] Admin can view and export weekly reports (XLSX, PDF)
- [ ] Admin can print 80 mm thermal receipts and PDF invoices
- [ ] Delivery staff mobile app captures GPS on every status update
- [ ] Delivery staff must provide POD before marking an order as Delivered

### Technical readiness

- [ ] Core OMS integration tests cover checkout, cancellation, delivery progression, and refund approval
- [ ] Celery jobs: daily availability reset, weekly report generation, notification dispatch
- [ ] Analytics events flowing through the configured provider
- [ ] Google Maps API key configured and ETA calls integrated
- [ ] Stripe as sole payment gateway; Khalti adapter removed or disabled
- [ ] i18n files (de/en) present for web and mobile
- [ ] Runtime configuration documented for local and production environments

### Documentation readiness

- [ ] Requirements reflect the restaurant OMS for Germany (no inventory, no warehouse, no Khalti)
- [ ] Architecture and infrastructure docs match FastAPI + Next.js + Flutter
- [ ] Implementation docs reflect the real repo status and updated gaps
