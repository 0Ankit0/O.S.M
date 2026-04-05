# User Stories

## 1. Customer Stories

### US-001: Customer Registration
**As a** customer, **I want to** register using my email address **so that** I can place orders on the platform.

**Acceptance Criteria:**
- Customer can register with email + password
- Social login via Google is supported
- Email is verified via confirmation link before account activation
- Duplicate email registrations are rejected with clear messaging
- Upon successful registration, customer is redirected to the homepage with a welcome notification

**Priority:** High | **Points:** 3

---

### US-002: Manage Default Delivery Address
**As a** customer, **I want to** save a default delivery address or use my current location **so that** checkout is fast and accurate.

**Acceptance Criteria:**
- Customer can set a default delivery address (used automatically at checkout)
- Customer can choose to use their current GPS location at checkout as an alternative
- System validates the address or location against configured delivery zones and rejects out-of-zone locations with a clear message
- Once an order is initiated, the delivery address is locked — the customer cannot change it
- Default address can be updated only when it is not linked to an active order

**Priority:** High | **Points:** 3

---

### US-003: Browse and Search Menu
**As a** customer, **I want to** browse the restaurant menu by category and keyword **so that** I can find items I want to order.

**Acceptance Criteria:**
- Storefront presents only **published** products that are marked as available today
- Products not available today are shown with a "Not available today" badge and cannot be added to cart
- Full-text search returns results within 500 ms at P95
- Results can be filtered by category and availability
- Results can be sorted by relevance, price, and newest
- Hierarchical category tree is navigable to any depth

**Priority:** High | **Points:** 5

---

### US-004: Add to Cart and Checkout
**As a** customer, **I want to** add items to my cart and proceed to checkout **so that** I can place my order.

**Acceptance Criteria:**
- Customer can add items with selected variant and quantity
- Cart persists across sessions (authenticated users only)
- Cart shows real-time prices, taxes, delivery fee (based on zone), and discount breakdown
- At checkout, system validates that all items are still published and available today
- System shows estimated delivery time via Google Maps ETA on the order confirmation page
- Delivery address is locked on checkout confirmation

**Priority:** High | **Points:** 8

---

### US-005: Apply Discount Coupon
**As a** customer, **I want to** apply a discount coupon at checkout **so that** I can save money on my order.

**Acceptance Criteria:**
- Customer enters coupon code and sees instant validation result (valid/invalid/expired)
- Valid coupons show the discount amount deducted from the total
- System enforces coupon rules: minimum order value, usage limits, validity period, applicable categories
- Only one coupon can be applied per order unless stacking is explicitly configured

**Priority:** Medium | **Points:** 3

---

### US-006: Track Order Status and ETA
**As a** customer, **I want to** view the real-time status and estimated delivery time of my order **so that** I know when to expect my food.

**Acceptance Criteria:**
- Order detail page shows current state and Google Maps-based estimated delivery time
- Timestamped milestone history is displayed (e.g., Confirmed, Preparing, OutForDelivery)
- Customer receives email notification at each major status change
- POD (signature or photo) is visible once order is delivered
- GPS location of each delivery staff status update is recorded (visible to admin)

**Priority:** High | **Points:** 5

---

### US-007: Cancel Order
**As a** customer, **I want to** cancel my order before the kitchen starts preparing it **so that** I can potentially receive a refund.

**Acceptance Criteria:**
- Cancel button is available only for orders in `Pending` state
- Once the order moves to `Preparing`, no customer-side cancellation is possible
- Cancellation requires a reason code from a predefined list
- A refund request is automatically created and submitted for admin review (no automatic refund)
- Customer receives email confirmation of cancellation and refund request submission

**Priority:** High | **Points:** 5

---

### US-008: Request Refund
**As a** customer, **I want to** request a refund for a delivered order **so that** I can raise an issue with my order.

**Acceptance Criteria:**
- Refund request option is available after the order is delivered
- Customer provides a mandatory reason; optional description
- System submits the request for admin review
- Customer receives email confirmation that the refund request has been received
- Customer can view refund request status (Requested, Approved, Denied, Completed) on the order detail page

**Priority:** High | **Points:** 3

---

### US-009: View Order History
**As a** customer, **I want to** view my past orders **so that** I can reorder items or check delivery details.

**Acceptance Criteria:**
- Order history shows all orders with status, date, total, and item summary
- Orders are sorted by date (newest first) with pagination
- Customer can click into any order for full details including milestones, POD, and review
- Customer can filter history by status (Active, Delivered, Cancelled)

**Priority:** Medium | **Points:** 3

---

### US-010: Submit Order Review and Rating
**As a** customer, **I want to** leave a review and rating for my delivered order **so that** I can share my experience.

**Acceptance Criteria:**
- Review option appears on the order detail page once the order status is `Delivered`
- Customer provides a star rating (1–5, required) and optional text comment and photo
- Each order has at most one review; customer can edit within 48 hours
- Review and average rating are visible on the restaurant storefront home page
- Review submission is not available for orders that are not in `Delivered` state

**Priority:** Medium | **Points:** 5

---

### US-011: Select Language
**As a** customer, **I want to** switch the platform language between German and English **so that** I can use the platform in my preferred language.

**Acceptance Criteria:**
- Language toggle is available on the storefront and customer portal
- Switching language instantly updates all UI strings, error messages, and labels
- Selected language persists across sessions in the user's account settings
- Currency displays as EUR with locale-appropriate formatting (€12,50 in de; €12.50 in en)
- Dates follow locale conventions (DD.MM.YYYY in de; MM/DD/YYYY in en)

**Priority:** High | **Points:** 3

---

### US-012: Manage Notification Preferences
**As a** customer, **I want to** control which notifications I receive **so that** I am not overwhelmed by messages.

**Acceptance Criteria:**
- Customer can toggle email notifications for promotional content
- Transactional notifications (order confirmation, status updates) cannot be disabled
- SMS toggle is visible but disabled (greyed out); no SMS are sent
- Preference changes take effect within 1 minute

**Priority:** Low | **Points:** 2

---

### US-013: Inspect Menu Item Details
**As a** customer, **I want to** view details of a menu item before adding it to cart **so that** I can compare variants and make a confident decision.

**Acceptance Criteria:**
- Customer can open item details from the menu without leaving the shopping flow
- Detail view shows description, available variants, and price
- Featured items are clearly distinguished from the rest of the menu
- Opening a menu item records a `catalog.product_viewed` analytics event

**Priority:** Medium | **Points:** 3

---

## 2. Delivery Staff Stories

### US-014: View Delivery Assignments
**As a** delivery staff member, **I want to** see my assigned deliveries for the day **so that** I can plan my delivery run.

**Acceptance Criteria:**
- Dashboard shows all assigned deliveries with customer name, address, order summary, and delivery window
- Deliveries are sorted by delivery zone proximity
- New assignments trigger email/push notification
- Staff can view a printable route sheet

**Priority:** High | **Points:** 5

---

### US-015: Update Delivery Status with Location
**As a** delivery staff member, **I want to** update order status as I progress through my delivery **so that** customers and operations can track progress.

**Acceptance Criteria:**
- Staff updates status through milestones: `PickedUp` → `OutForDelivery` → `Delivered`
- **Each status update captures the GPS coordinates (latitude, longitude) of the staff member at that moment**
- Each update records timestamp and staff identity
- System enforces milestone ordering — states cannot be skipped
- Status updates trigger customer email notifications

**Priority:** High | **Points:** 3

---

### US-016: Capture Proof of Delivery
**As a** delivery staff member, **I want to** capture the recipient's signature or a photo **so that** delivery is confirmed before I mark it complete.

**Acceptance Criteria:**
- **Staff must capture either an electronic signature or at least one photo before marking the order as `Delivered`**
- System blocks the `Delivered` status transition until POD is provided
- POD is uploaded to object storage and linked to the order record
- If offline, POD is stored locally and synced when connectivity resumes
- POD is visible to the customer and admin on the order detail page

**Priority:** High | **Points:** 8

---

### US-017: Record Failed Delivery
**As a** delivery staff member, **I want to** record a failed delivery attempt **so that** operations can follow up with the customer.

**Acceptance Criteria:**
- Staff selects failure reason (customer unavailable, wrong address, access issue)
- Staff can add optional notes
- System notifies customer of failed attempt via email
- After 3 failed attempts, admin is alerted for manual resolution

**Priority:** High | **Points:** 5

---

## 3. Operations Manager Stories

### US-018: Monitor Order Dashboard
**As an** operations manager, **I want to** view a real-time order and delivery dashboard **so that** I can identify bottlenecks and SLA risks.

**Acceptance Criteria:**
- Dashboard shows: orders pending, orders being prepared, orders out for delivery, completed today
- SLA countdown is visible per order with colour-coded urgency (green/yellow/red)
- Manager can filter by delivery zone and date range
- Dashboard auto-refreshes every 30 seconds

**Priority:** High | **Points:** 5

---

### US-019: Reassign Delivery Staff
**As an** operations manager, **I want to** reassign deliveries to different staff members **so that** I can balance workload or handle staff absences.

**Acceptance Criteria:**
- Manager can select one or more orders and reassign to another available staff member
- Reassignment is allowed only for orders in `ReadyForDispatch` or `PickedUp` states
- Original staff member is notified of reassignment
- New staff member receives the delivery details
- Reassignment is logged in the audit trail

**Priority:** High | **Points:** 5

---

### US-020: Manage Delivery Zones
**As an** operations manager, **I want to** configure delivery zones **so that** the system knows which areas we service and the associated fees.

**Acceptance Criteria:**
- Manager can create, edit, and deactivate delivery zones
- Each zone has: name, geographic boundary (postcodes or polygon), **delivery fee**, minimum order value, SLA target
- Deactivating a zone prevents new orders to that area but does not affect active orders
- Zone changes are versioned with effective date
- Delivery fee is automatically applied at checkout based on the customer's zone

**Priority:** Medium | **Points:** 5

---

### US-021: View Delivery Performance Reports
**As an** operations manager, **I want to** view delivery performance reports **so that** I can identify improvement areas and high performers.

**Acceptance Criteria:**
- Reports show: on-time delivery rate, average delivery time, failed delivery rate, staff utilisation
- Reports can be filtered by staff member, delivery zone, and date range
- Staff performance ranking is available with key metrics
- Reports can be exported in Excel (XLSX), CSV, and PDF formats

**Priority:** Medium | **Points:** 5

---

## 4. Admin Stories

### US-022: Manage Product Catalog
**As an** admin, **I want to** manage the product catalog **so that** customers can browse and order current dishes.

**Acceptance Criteria:**
- Admin can create, edit, and archive products and categories
- Admin can **toggle a product's published state directly from the product list page** (inline toggle, no full edit needed)
- Only published products appear on the customer storefront
- Category hierarchy supports unlimited depth
- Product changes are reflected in search results within 5 seconds

**Priority:** High | **Points:** 5

---

### US-023: Toggle Daily Product Availability
**As an** admin, **I want to** mark a product as unavailable for today **so that** customers cannot order a dish when an ingredient is out.

**Acceptance Criteria:**
- Admin can toggle daily availability per product from the product list page
- Products marked unavailable today show "Not available today" on the storefront and cannot be added to cart
- Daily availability resets to `available` automatically at the start of each day (configurable)
- Toggling daily availability does not change the product's published state
- Changes take effect within 30 seconds

**Priority:** High | **Points:** 3

---

### US-024: Review and Approve Refund Requests
**As an** admin, **I want to** review and approve or deny refund requests **so that** I can decide whether a customer deserves a refund after reviewing their order.

**Acceptance Criteria:**
- Admin sees all pending refund requests in the refund management dashboard
- Each request shows: order details, items ordered, total paid, customer reason, and order status at time of request
- Admin approves or denies with a mandatory internal note
- On approval, system initiates a full-order refund through Stripe; no partial refunds
- Customer receives email notification with outcome and admin note (translated to customer's language)
- Once a meal has been prepared, admin policy is to deny refunds; the system does not enforce this automatically but records the decision

**Priority:** High | **Points:** 5

---

### US-025: Send Custom Notification to Customers
**As an** admin, **I want to** compose and send a custom notification message to customers **so that** I can communicate important updates like closures or new menu items.

**Acceptance Criteria:**
- Admin can compose a subject and body for a custom email message
- Admin can target all customers or a filtered segment (by zone, by last order date range)
- Admin can schedule the message for a future time or send immediately
- System records sender, timestamp, recipient count, and message content for audit
- Sent messages cannot be recalled; admin is prompted to confirm before sending

**Priority:** Medium | **Points:** 3

---

### US-026: Manage Coupons and Promotions
**As an** admin, **I want to** create and manage discount coupons **so that** I can run marketing campaigns.

**Acceptance Criteria:**
- Admin can create coupons with: code, discount type (percentage/fixed/free delivery), value, min order, validity dates, usage limits
- Admin can view coupon usage statistics
- Admin can deactivate coupons immediately
- Coupon creation and changes are audited

**Priority:** Medium | **Points:** 3

---

### US-027: Manage Delivery Staff Accounts
**As an** admin, **I want to** onboard and manage delivery staff accounts **so that** they can access their operational dashboards.

**Acceptance Criteria:**
- Admin can create staff accounts with role (Delivery Staff, Operations Manager)
- Admin can assign staff to delivery zones
- Admin can deactivate staff accounts (soft delete, preserving audit trail)
- Staff account changes are audited with admin identity and timestamp

**Priority:** High | **Points:** 3

---

### US-028: View Weekly Sales Report
**As an** admin, **I want to** view and export the weekly sales report **so that** I can track business performance.

**Acceptance Criteria:**
- Weekly report is automatically generated each Monday covering the previous Mon–Sun
- Report includes: total orders, revenue, top 5 products, delivery performance summary, refund summary
- Report is accessible from the admin dashboard
- Report can be optionally emailed to configured recipients
- Report can be exported in **Excel (XLSX)**, CSV, and PDF formats

**Priority:** Medium | **Points:** 5

---

### US-029: Print Invoice and Thermal Receipt
**As an** admin, **I want to** print an invoice or a compact receipt for an order **so that** I can provide documentation to the customer or kitchen.

**Acceptance Criteria:**
- Admin can click "Print Invoice" on the order detail page to generate and print a full PDF invoice
- Invoice includes: order ID, date, itemised list with prices, taxes, delivery fee, discount, and total
- Admin can click "Print Receipt" to generate a layout optimised for **80 mm thermal printers**
- Receipt includes: restaurant name, order ID, date/time, items with quantities and prices, subtotal, delivery fee, discount, total, payment confirmation
- Both print actions produce output immediately without server round-trip (client-side rendering of print view)

**Priority:** Medium | **Points:** 5

---

### US-030: Manage Notification Templates
**As an** admin, **I want to** manage notification templates **so that** customer and staff communications are consistent and professional in both German and English.

**Acceptance Criteria:**
- Admin can create and edit templates for each event type in both German and English
- Templates support variable placeholders ({{order_id}}, {{customer_name}}, {{eta}}, etc.)
- Templates are versioned with rollback to previous version
- Admin can preview templates with sample data before publishing
- Language selection determines which template variant is sent to each customer

**Priority:** Low | **Points:** 3

---

### US-031: View Platform Analytics
**As an** admin, **I want to** view platform-wide analytics **so that** I can make data-driven business decisions.

**Acceptance Criteria:**
- Dashboard shows: total revenue, order volume, average order value, top products, refund rate, average review rating
- Metrics default to **weekly view** with options for day/month/year
- Admin can drill down by product, category, delivery zone
- Dashboard data refreshes at most every 5 minutes

**Priority:** Medium | **Points:** 5

---

### US-032: Configure Platform Settings
**As an** admin, **I want to** configure global platform settings **so that** business rules are enforced consistently.

**Acceptance Criteria:**
- Admin can configure: tax rates, default delivery fee fallback, max delivery attempts, preparation time estimate, daily availability reset time
- Language default can be set for the platform
- Google Maps API key and Stripe keys are configurable via environment settings
- Configuration changes are versioned with rollback capability
- Changes take effect within 1 minute without service restart
- All configuration changes are audited

**Priority:** Medium | **Points:** 3

---

### US-033: View Audit Logs
**As an** admin, **I want to** view audit logs **so that** I can investigate incidents and ensure compliance.

**Acceptance Criteria:**
- Audit log captures: actor, action, resource, timestamp, before/after values
- Logs are searchable by actor, action type, resource type, and date range
- Logs are immutable — no edit or delete capability
- Logs are retained for at least 1 year (GDPR-compliant retention policy)

**Priority:** Medium | **Points:** 3

---

## 5. Finance Stories

### US-034: View Payment Reconciliation
**As a** finance team member, **I want to** view daily payment reconciliation reports **so that** I can ensure all payments are accounted for.

**Acceptance Criteria:**
- Report shows: payment captures, refunds (admin-approved), net settlement, discrepancies
- Discrepancies exceeding configured tolerance are flagged for manual review
- Report can be filtered by date range
- Report can be exported in Excel (XLSX) and CSV formats

**Priority:** Medium | **Points:** 5

---

### US-035: Process Manual Refund
**As a** finance team member, **I want to** execute admin-approved refunds **so that** customers receive their money.

**Acceptance Criteria:**
- Finance can process refunds for orders where admin has approved the refund request
- System validates refund amount does not exceed original payment (full order only, no partial)
- Manual refund processing is logged in the audit trail
- Customer receives email confirmation of completed refund

**Priority:** Medium | **Points:** 3

---

## 6. Cross-Cutting Stories

### US-036: Receive Real-Time Email Notifications
**As a** user (customer or staff), **I want to** receive timely email notifications for relevant events **so that** I stay informed and can act promptly.

**Acceptance Criteria:**
- Notifications are dispatched within 60 seconds of the triggering event (P95)
- Failed notification delivery is retried up to 3 times with 30-second intervals
- Notification delivery receipts are recorded for audit
- Email content is delivered in the customer's selected language (German or English)

**Priority:** High | **Points:** 5

---

### US-037: Idempotent API Operations
**As a** developer, **I want** all mutating API operations to be idempotent **so that** retries and network failures do not cause duplicate side effects.

**Acceptance Criteria:**
- All POST/PUT/PATCH endpoints require `Idempotency-Key` header
- Duplicate requests within 24-hour TTL return cached response without re-executing business logic
- Idempotency scope is `(user_id, route, key)`
- Expired idempotency keys are cleaned up automatically

**Priority:** High | **Points:** 5

---

### US-038: Switch Analytics Provider
**As a** developer or operator, **I want to** switch analytics providers by configuration **so that** the OMS can move between PostHog, Mixpanel, and future tools without rewriting feature logic.

**Acceptance Criteria:**
- Backend, web, and mobile use the same analytics abstraction pattern
- Provider selection is controlled by environment configuration
- Unknown or disabled providers fail safely without breaking customer or admin flows
- OMS business events such as `catalog.product_viewed`, `cart.item_added`, and `order.created` continue to fire from the same call sites after a provider switch

**Priority:** Medium | **Points:** 3

---

### US-039: Review Moderation
**As an** admin, **I want to** moderate customer reviews **so that** inappropriate content is not shown on the storefront.

**Acceptance Criteria:**
- Admin can view all submitted reviews with order reference, rating, and text
- Admin can hide a review (hidden reviews are removed from storefront but retained for audit)
- Admin can flag a review for follow-up
- Average rating and total review count on the storefront update within 5 minutes of moderation action

**Priority:** Low | **Points:** 3

---

### US-040: Event-Driven Architecture
**As a** developer, **I want** all major state changes to emit domain events **so that** services are decoupled and the system is extensible.

**Acceptance Criteria:**
- Every order state transition emits a domain event with event type, payload, and correlation ID
- Events are published within 2 seconds of the state change (P95)
- Failed async delivery lands in retry/dead-letter handling for manual redrive
- Event consumers are idempotent — duplicate events are safely ignored

**Priority:** High | **Points:** 8

