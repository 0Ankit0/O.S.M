# Code Guidelines

## Overview

Development standards, conventions, and best practices for the restaurant OMS codebase. The documented target is a Django monolith with Tailwind-powered server-rendered templates, PostgreSQL, Redis, Celery, and provider abstractions for payments, notifications, analytics, maps, and storage.

## Technology Stack

| Area | Technology | Notes |
|---|---|---|
| Web runtime | Django | Routing, ORM, forms, sessions, permissions, template rendering |
| Frontend styling | Tailwind CSS | Shared tokens, layout primitives, utility-first template styling |
| Background jobs | Celery | Async workflows and scheduled jobs |
| Database | PostgreSQL | Canonical transactional datastore |
| Cache / coordination | Redis | Cache, idempotency support, short-lived coordination |
| Files | Local or S3-compatible storage | Images, POD artifacts, reports, invoices |

## Project Structure

```text
oms/
├── manage.py
├── pyproject.toml
├── oms/
│   ├── settings/
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── accounts/
│   ├── catalog/
│   ├── orders/
│   ├── payments/
│   ├── delivery/
│   ├── notifications/
│   └── reporting/
├── templates/
│   ├── base_user.html
│   ├── base_admin.html
│   └── partials/
│       ├── header.html
│       ├── footer.html
│       ├── admin_sidebar.html
│       ├── breadcrumbs.html
│       └── alerts.html
├── static/
│   └── src/
│       ├── css/
│       └── js/
└── docs/
```

## Django Application Conventions

| Concern | Guidance |
|---|---|
| App boundaries | Group code by business domain, not by technical layer alone |
| Views | Prefer class-based or well-structured function views with clear permission boundaries |
| Forms | Use Django forms or form classes for validation-heavy browser flows |
| Services | Put provider calls, orchestration, and cross-model workflows in service modules |
| Templates | Every page extends `base_user.html` or `base_admin.html` |
| Permissions | Use Django groups and permissions, with explicit staff/admin checks |
| Tasks | Use Celery for slow, scheduled, or retryable work |

## Frontend and Layout Rules

### Base templates

- `base_user.html` is the only shell for public and customer-facing pages.
- `base_admin.html` is the only shell for staff and admin-facing pages.
- Child templates must not copy headers, sidebars, or global wrappers into leaf pages.

### Shared partials

Use partials for repeated UI chrome:

- headers
- footers
- alerts
- breadcrumbs
- admin sidebar
- page title and actions

### Tailwind usage

- define shared colors, spacing, typography, and breakpoints in the Tailwind config
- keep template classes intentional and composable
- use reusable component partials before introducing custom JavaScript-heavy widgets
- ensure both layouts are responsive and visually distinct

## Route and Template Mapping

| Route Area | Layout | Notes |
|---|---|---|
| `/` storefront and menu pages | `base_user.html` | Landing, categories, products |
| `/account/*` | `base_user.html` | Profile, addresses, orders, preferences |
| `/checkout/*` | `base_user.html` | Checkout and payment steps |
| `/orders/*` customer pages | `base_user.html` | Customer order detail and tracking |
| `/dashboard/*` | `base_admin.html` | Staff and admin portal |
| `/admin/*` internal tools if retained | `base_admin.html` or stock admin | Use only where it complements the custom portal |

## API and Interaction Rules

- prefer HTML views and redirects for primary browser interactions
- use JSON endpoints only for progressive enhancement, polling, or external integrations
- protect browser mutations with CSRF and authentication
- apply idempotency safeguards to checkout and payment-sensitive flows

## Testing Guidance

| Area | Suggested Coverage |
|---|---|
| Views and permissions | Route access by role, redirects, forbidden responses |
| Templates | Correct layout inheritance and required page blocks |
| Forms | Validation, error states, localization, and success flows |
| Services | Payment, notification, ETA, and reporting orchestration |
| Tasks | Retry behavior, scheduled jobs, and export generation |
| UI flows | Customer storefront flow and admin operational flow |

## Non-Negotiables

- PostgreSQL is the source of truth for business state.
- Redis is never the canonical business datastore.
- The custom admin/staff portal is part of the product, not an afterthought.
- Every new page must clearly belong to either the user layout or the admin layout.
- Tailwind usage must reinforce a consistent system rather than ad hoc page styling.
