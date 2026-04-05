# Requirements Document

## 1. Introduction

### 1.1 Purpose

This document defines the functional and non-functional requirements for a restaurant-focused Order Management System (OMS) implemented with FastAPI, Next.js, and Flutter. The platform is designed for a restaurant operating in Germany, managing the complete menu-to-delivery lifecycle using internal delivery personnel. The system prioritises menu-first browsing, zone-based delivery pricing, and a streamlined post-delivery settlement model where meals are final once prepared.

### 1.2 Scope

The system covers:
- Restaurant storefront with menu-first browsing (published items only)
- Customer account management with default delivery address and live location support
- Product catalog with daily availability toggling (no inventory tracking)
- Cart, checkout, and payment processing (Stripe; no Khalti)
- Order lifecycle management with status-driven tracking and Google Maps ETA
- Internal delivery assignment with GPS location capture on status change
- Proof of delivery capture (signature or photo) before status update
- Admin-gated refund processing (no automatic refunds; no partial refunds)
- Email-only notifications with owner-defined custom messages
- Weekly analytics reports with Excel and PDF export
- Invoice and 80 mm thermal receipt printing
- Internationalisation: German and English (i18n)
- Review and rating system (per completed order)
- Administrative operations and platform configuration

**Out of scope:**
- Inventory / stock tracking
- Warehouse fulfillment (pick, pack, ship)
- Return pickup
- Return inspection
- Partial refunds
- SMS notifications (disabled; infrastructure present but off by default)
- Push notifications (future phase)
- Table reservations
- Khalti payment gateway
- Multi-warehouse management

### 1.3 Definitions

| Term | Definition |
|------|------------|
| **OMS** | Order Management System — central platform for order lifecycle |
| **POD** | Proof of Delivery — signature or timestamped photo confirming delivery |
| **Delivery Assignment** | Binding of a confirmed order to an internal delivery staff member |
| **Delivery Zone** | Geographic area with a fixed delivery fee and SLA target |
| **Idempotency Key** | Client-generated unique key ensuring duplicate requests are safely ignored |
| **SLA** | Service Level Agreement — contractual performance target |
| **DLQ** | Dead Letter Queue — holding area for failed async processing |
| **Daily Availability** | Per-product flag toggled by admin when an ingredient or dish is unavailable for the day |
| **Published** | Product state visible to customers on the storefront |
| **Admin Refund** | Manual refund decision made by an admin after order review; never automatic |

---

## 2. Functional Requirements

### 2.1 Customer Management Module

#### FR-CM-001: Customer Registration
- System shall allow customers to register using email and password
- System shall support social login via Google
- System shall verify email via confirmation link before account activation
- System shall enforce unique email constraints

#### FR-CM-002: Customer Profile
- Customers shall manage their profile (name, email, phone, avatar)
- Customers shall view their complete order history with status
- Customers shall manage notification preferences (email only; SMS toggle present but disabled)

#### FR-CM-003: Address Management
- Customers shall save a default delivery address (used automatically at checkout)
- Customers may alternatively choose to use their current GPS location at checkout
- System shall validate address serviceability against configured delivery zones and reject out-of-zone addresses
- Once an order is initiated (status moves past `Pending`), the delivery address is locked and cannot be changed
- Customers may update their default address only when it is not linked to an active order

#### FR-CM-004: Authentication
- System shall implement JWT-based authentication via the FastAPI auth module
- System shall support session management with configurable TTL
- System shall enforce password complexity policies (min 8 chars, mixed case, digit, symbol)
- System shall support multi-factor authentication for customer accounts

---

### 2.2 Product Catalog Module

#### FR-PC-001: Category Management
- System shall support hierarchical categories with **unlimited depth** (no maximum level restriction)
- Admin shall create, edit, reorder, and archive categories
- Categories shall support custom display attributes and images
- Categories may be nested to any depth; the storefront renders the full tree

#### FR-PC-002: Product Management
- Admin shall create products with title, description, images, and pricing
- Products shall support multiple variants (size, portion, configuration)
- Each variant shall have an independent SKU and price
- Products shall support featured placement for storefront merchandising
- **Only published products are visible to customers** on the storefront
- Admin shall toggle the published state of any product directly from the product list page (inline toggle, no full edit required)
- Admin shall toggle **daily availability** per product (e.g., dish unavailable today due to missing ingredient); toggling availability does not change the published state
- Products with daily availability set to `unavailable` are shown as "Not available today" and cannot be added to cart

#### FR-PC-003: Product Search and Discovery
- System shall provide product search through application-backed filtering and full-text search abstractions
- System shall support filters by category, price range, and availability
- System shall support sort by relevance, price, popularity, and newest
- Search results shall only return **published** products with daily availability `available`
- System shall return search results within 500 ms at P95

> **Note:** Inventory tracking, stock reservations, low-stock alerts, and manual stock adjustments are **not part of this system**. Product availability is managed manually by admin on a per-day basis.

---

### 2.3 Shopping Cart and Checkout Module

#### FR-SC-001: Cart Management
- Customers shall add, remove, and update quantities of cart items
- Cart shall persist across sessions (authenticated users only; no guest cart merge)
- System shall display real-time price updates reflecting current catalog prices
- System shall validate item published and daily availability status on every cart view and at checkout

#### FR-SC-002: Checkout Process
- System shall validate all cart items for published and daily availability before proceeding
- System shall calculate line item totals, applicable taxes, and delivery fees based on the customer's delivery zone
- System shall apply discount coupons and promotional offers with stacking rules
- System shall enforce minimum order value constraints per delivery zone
- **Customer's delivery address is locked once checkout is confirmed; no address changes are permitted after this point**

#### FR-SC-003: Discount and Coupon Engine
- Admin shall create coupons with configurable rules: percentage, fixed amount, free delivery
- Coupons shall support validity period, usage limits (global and per-customer), and minimum order value
- System shall validate coupon applicability at checkout and reject expired or exhausted coupons
- System shall support category-specific and product-specific discounts

---

### 2.4 Order Management Module

#### FR-OM-001: Order Creation
- System shall create orders upon successful payment capture
- System shall generate globally unique order IDs (prefixed, human-readable)
- System shall record complete order snapshot: items, prices, taxes, discounts, delivery fee, payment reference
- All mutating order endpoints shall require an `Idempotency-Key` header

#### FR-OM-002: Order Tracking
- Customers shall view real-time order status through all lifecycle states
- System shall display timestamped milestone history for each order
- System shall display **estimated delivery time** using Google Maps Distance Matrix API based on restaurant location, delivery zone, and current traffic
- Customers shall receive email notifications at every major status transition

#### FR-OM-003: Order Cancellation
- Customers may cancel orders only in `Pending` state (before the kitchen confirms preparation)
- Once the kitchen marks the order as `Preparing`, no customer-initiated cancellation is permitted
- Cancellation of paid orders shall trigger an **admin review** for refund (no automatic refund)
- Cancellation reason code shall be mandatory

#### FR-OM-004: Order Modification
- **Delivery address cannot be changed once an order is initiated (past `Pending` state)**
- System shall log all modifications with before/after values and actor identity

---

### 2.5 Payment Module

#### FR-PM-001: Payment Gateway Integration
- System shall integrate with **Stripe** as the primary payment gateway
- System shall support credit/debit cards and digital wallets (Apple Pay, Google Pay via Stripe)
- Gateway failover to a secondary Stripe configuration or manual fallback may be configured

#### FR-PM-002: Payment Processing
- System shall perform payment authorization at checkout initiation
- System shall capture payment upon order confirmation
- System shall handle transient payment failures with exponential backoff (base 1 s, max 60 s, 3 retries)
- All payment operations shall be idempotent using gateway-provided idempotency keys
- System shall store payment transaction records with gateway reference IDs

#### FR-PM-003: Refund Processing
- **Refunds are not automatic** — every refund requires explicit admin approval
- Admin shall review refund requests and approve or deny them through the admin dashboard
- Once a meal has been prepared (`Preparing` or later state), refund requests will typically be denied by admin policy
- **No partial refunds** — refunds are full-order amounts only
- System shall track refund status: `Requested`, `Approved`, `Processing`, `Completed`, `Denied`
- Customer receives email notification on refund status change
- Failed refund processing shall alert admin after 3 retry attempts

#### FR-PM-004: Payment Reconciliation
- System shall reconcile payment captures against Stripe settlement reports daily
- System shall flag discrepancies exceeding configurable tolerance for manual review
- System shall generate payment reconciliation reports accessible to the finance role

---

### 2.5 Delivery Management Module

#### FR-DM-001: Delivery Assignment
- System shall assign orders to available internal delivery staff based on delivery zone
- System shall consider staff capacity (max orders per run) when assigning
- System shall support manual reassignment by operations manager
- System shall notify assigned staff via email with delivery details

#### FR-DM-002: Delivery Zone and Fee Management
- Admin shall configure delivery zones with geographic boundaries (polygon or PIN/postcode list)
- Each zone shall have: name, geographic boundary, **delivery fee**, minimum order value, and SLA target
- **Delivery fee is automatically calculated and applied at checkout based on the customer's zone**
- Deactivating a zone prevents new orders to that area but does not affect active orders
- Zone changes are versioned with effective date

#### FR-DM-003: Delivery Execution with Location
- Delivery staff shall update order status through milestones: `PickedUp` → `OutForDelivery` → `Delivered`
- **Each status update shall record the GPS coordinates (latitude, longitude) of the delivery staff at the time of the update**
- Status updates shall also record timestamp and staff identity
- System shall enforce milestone ordering — states cannot be skipped
- Status updates trigger customer email notifications

#### FR-DM-004: Proof of Delivery
- **Before marking an order as `Delivered`, delivery staff must capture either an electronic signature from the recipient or at least one timestamped photo at the delivery location** (one is sufficient)
- System shall upload POD artifacts to local or S3-compatible object storage and link to the order record
- POD shall be accessible to customer and admin
- System shall support offline POD capture with sync-on-reconnect
- POD upload failure triggers retry; after 3 failures, alert sent to admin

#### FR-DM-005: Estimated Delivery Time
- System shall integrate with **Google Maps Distance Matrix API** to calculate estimated delivery time
- Estimated delivery time shall be displayed to the customer on the order tracking page and in email notifications
- ETA shall account for restaurant preparation time (configurable per order type) plus transit time

#### FR-DM-006: Failed Delivery Handling
- Delivery staff shall record failed delivery reason (customer unavailable, wrong address, access issue)
- Customer shall be notified of failed attempt via email
- After 3 failed attempts, admin is alerted for manual resolution

---

### 2.6 Refund Module

#### FR-RF-001: Refund Request
- Customers may submit a refund request with a mandatory reason after order delivery
- Refund requests are visible to admin in the refund management dashboard

#### FR-RF-002: Admin Refund Decision
- Admin shall review each refund request and **approve or deny** it manually
- System shall present the order details, payment amount, and customer reason to the admin reviewer
- On approval, system initiates full-order refund through the original payment gateway
- On denial, customer is notified via email with the reason
- **No automated, no partial, and no return-pickup-based refunds exist in this system**

---

### 2.7 Notification Module

#### FR-NM-001: Email Notifications
- System shall send transactional emails through the configured email provider adapter
- System shall support HTML email templates with dynamic content injection
- System shall track email delivery and bounce rates
- **Email is the only active notification channel in this phase**

#### FR-NM-002: SMS Notifications (Disabled)
- SMS infrastructure shall be present in the codebase but **disabled by default** (`SMS_ENABLED=false`)
- No SMS messages shall be sent unless the flag is explicitly enabled by the operator
- This requirement exists to allow future activation without code changes

#### FR-NM-003: Custom Notification Messages
- **The restaurant owner/admin shall be able to compose and send custom notification messages to customers** (e.g., "We are closed today", "New seasonal menu available")
- Custom messages are sent via email to all customers or a filtered segment (e.g., by zone or last order date)
- Custom messages are stored with sender identity, timestamp, and recipient count for audit
- Admin may schedule custom messages for a future send time

#### FR-NM-004: Notification Templates
- Admin shall manage email notification templates for each event type
- Templates shall support variable substitution (order ID, customer name, delivery window, ETA)
- System shall version templates and support rollback to previous versions
- Admin can preview templates with sample data before publishing

---

### 2.8 Analytics and Reporting Module

#### FR-AR-001: Sales Dashboard
- System shall provide sales metrics: total orders, revenue, average order value, top products
- Dashboard shall support date range filters with **weekly view as the default**
- System shall break down sales by product, category, and delivery zone

#### FR-AR-002: Delivery Performance
- System shall track delivery KPIs: on-time delivery rate, average delivery time, failed delivery rate
- System shall rank delivery staff by performance metrics

#### FR-AR-003: Weekly Reports
- System shall generate **weekly summary reports** automatically (covering Mon–Sun)
- Weekly report content: total orders, revenue, top 5 products, delivery performance summary, refund summary
- Reports are accessible from the admin dashboard and optionally emailed to configured recipients

#### FR-AR-004: Export
- System shall support report export in **Excel (XLSX)**, CSV, and PDF formats
- System shall store generated reports in local or S3-compatible object storage with configurable retention (default 90 days)

#### FR-AR-005: Invoice Printing
- System shall generate printable invoices for each order in PDF format
- Invoices shall include: order ID, date, itemised list with prices, taxes, delivery fee, discount, total, and payment method

#### FR-AR-006: 80 mm Thermal Receipt Printing
- System shall generate a compact receipt layout optimised for **80 mm thermal printers** (ESC/POS or PDF at 80 mm width)
- Receipt content: restaurant name, order ID, date/time, items with quantities and prices, subtotal, delivery fee, discount, total, and payment confirmation
- Receipt shall be printable from the admin order detail page with a single "Print Receipt" button

#### FR-AR-007: Analytics Event Taxonomy
- System shall emit business-level analytics events for storefront and OMS operations
- Required event namespaces: `catalog`, `cart`, `checkout`, `order`, `delivery`, `refund`, `admin`
- Minimum events: `catalog.product_viewed`, `cart.item_added`, `checkout.started`, `order.created`, `order.cancelled`, `delivery.status_updated`, `refund.requested`, `refund.approved`, `admin.product_updated`

---

### 2.9 Review and Rating Module

#### FR-RV-001: Order Review
- Customers shall be able to submit a review and star rating (1–5) **per completed order**
- Reviews are associated with the order, not with individual products directly
- Review submission is only available for orders with `Delivered` status
- Each order may have at most one review; customers may edit their review within 48 hours

#### FR-RV-002: Review Content
- Review shall include: star rating (required, 1–5), optional text comment, and optional photo upload
- Reviews shall be stored with the customer identity, timestamp, and order reference

#### FR-RV-003: Review Moderation
- Admin shall be able to hide or flag reviews for inappropriate content
- Hidden reviews are not shown on the storefront but are retained for audit
- System shall display average rating and total review count on the restaurant storefront home page

---

### 2.10 Internationalisation (i18n) Module

#### FR-I18N-001: Supported Languages
- The platform shall support **German (de) and English (en)** as selectable UI languages
- Language selection shall be available on the storefront, customer portal, and admin dashboard
- Selected language shall be persisted per user account and remembered across sessions

#### FR-I18N-002: Translation Coverage
- All customer-facing UI strings, error messages, and email templates shall be available in both German and English
- Admin-facing strings shall be available in both languages
- Product titles and descriptions may be entered in one language; translation is the owner's responsibility
- Date, time, currency (EUR), and number formats shall follow the selected locale conventions

#### FR-I18N-003: Locale-Aware Formatting
- Currency shall be displayed as EUR with locale-appropriate symbol and decimal separator (e.g., `€12,50` in de; `€12.50` in en)
- Dates and times shall follow locale conventions (DD.MM.YYYY in de; MM/DD/YYYY or ISO in en)

---

### 2.11 Admin and Operations Module

#### FR-AM-001: Role-Based Access Control
- System shall enforce RBAC with roles: Customer, Delivery Staff, Operations Manager, Finance, Admin
- Admin shall configure permissions per role at the API endpoint level
- System shall maintain audit logs for all admin actions

#### FR-AM-002: Platform Configuration
- Admin shall configure global settings: tax rates, delivery fees per zone, reservation TTL (for session, not stock), max delivery attempts, preparation time estimates
- Configuration changes shall be versioned with rollback capability

#### FR-AM-003: Staff Management
- Admin shall onboard and offboard delivery staff accounts
- Admin shall assign staff to delivery zones
- System shall track staff activity: deliveries completed, performance score

#### FR-AM-004: Content Management
- Admin shall manage promotional banners and announcements
- Admin shall schedule promotional campaigns with start/end dates

---

## 3. Non-Functional Requirements

### 3.1 Performance

| Requirement | Target |
|-------------|--------|
| API response time | < 500 ms (P95) |
| Product search results | < 500 ms (P95) |
| Order confirmation latency | < 3 seconds end-to-end |
| Concurrent users | 10,000+ |
| Orders per minute | 500+ |
| POD photo upload | < 5 seconds for 5 MB image |

### 3.2 Scalability
- FastAPI API instances shall scale horizontally behind a reverse proxy or load balancer
- Celery workers shall scale independently by queue type and workload
- PostgreSQL replicas may be added for reporting and analytics queries
- Redis deployment may be scaled for cache and idempotency workloads
- Object storage shall support growth without application-level path changes

### 3.3 Availability
- 99.9 % platform availability (rolling 30 days)
- Production deployments shall support redundant API and worker processes
- Database and cache layers shall support resilient deployment topologies appropriate to the selected infrastructure
- Zero-downtime deployments via blue-green and canary strategies
- Graceful degradation: payment gateway retry, email notification retry, read-replica promotion

### 3.4 Security
- HTTPS/TLS 1.3 for all communications
- PCI-DSS compliance for payment data (tokenisation via Stripe, no raw card storage)
- Data encryption at rest for database, object storage, and cached sensitive material
- Data encryption in transit (TLS for all internal service communication)
- MFA support for admin and staff accounts
- Network isolation and firewall controls shall be enforced by the chosen deployment environment
- Regular security audits and penetration testing
- GDPR compliance for customer data (applicable as the platform operates in Germany)

### 3.5 Reliability
- Automated daily database snapshots with 30-day retention
- Async workflows shall support retry and dead-letter handling for failed processing
- Circuit breaker pattern for payment gateway and notification calls

### 3.6 Maintainability
- Environment-aware configuration and deployment automation shall be maintained for dev, staging, and production
- Structured JSON logging with correlation IDs shall be used across backend and workers
- Observability shall support request tracing, metrics, and health checks
- Health check endpoints for all services
- Feature flags and runtime toggles shall be supported through the application configuration layer

### 3.7 Usability
- Mobile-responsive customer portal in Next.js
- Lightweight mobile-optimised interface for delivery staff (Flutter)
- WCAG 2.1 AA accessibility compliance
- **Multi-language support: German (de) and English (en)** with locale-aware formatting for EUR currency, dates, and numbers

---

## 4. System Constraints

### 4.1 Technical Constraints
- FastAPI remains the primary backend runtime
- Next.js remains the primary web runtime
- Flutter remains the primary mobile runtime
- PostgreSQL remains the canonical transactional datastore
- Redis remains auxiliary for cache, idempotency, and hot-path coordination
- Background workflows shall run through Celery or equivalent queue-backed workers
- API-first design with OpenAPI 3.1 specification
- Google Maps Distance Matrix API for delivery ETA calculations
- Stripe as the sole payment gateway

### 4.2 Business Constraints
- Internal delivery team only — no third-party carrier integration
- Delivery address is locked once an order is initiated — no customer-side address changes post-checkout
- Once a meal is prepared, refunds are at admin discretion and are typically denied
- No partial refunds under any circumstance
- Delivery zones must be explicitly configured before orders can be accepted
- Storefront shows only published, daily-available products
- No inventory tracking — product availability is managed manually by admin
- No warehouse management — restaurant prepares and hands off directly to delivery staff
- No table reservations
- SMS notifications disabled by default; email is the sole active channel in this phase
- Currency is EUR; platform operates in Germany and must comply with GDPR

### 4.3 Regulatory Constraints
- GDPR compliance (data subject rights, lawful basis for processing, data minimisation)
- PCI-DSS compliance via Stripe tokenisation (no raw card data stored)
- Data encryption at rest and in transit
- Electronic signature or photo compliance for proof of delivery
- VAT/tax rules applicable to German restaurant operations
