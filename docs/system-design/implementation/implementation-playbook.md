# Implementation Playbook

## Overview

This playbook tracks how the restaurant OMS should be implemented in a Django monolith. Django owns both backend behavior and frontend delivery, using server-rendered templates styled with Tailwind CSS. PostgreSQL remains the canonical datastore, Redis supports caching and coordination, Celery runs background workflows, and provider abstractions isolate payments, notifications, analytics, maps, and storage.

## Delivery Tracks

### Track 1. Foundation and doc realignment

Goal:

- align architecture docs with the Django monolith target
- establish Django apps and shared project conventions
- define the dual-layout template system for customer and admin experiences

Outcome:

- Django is the documented source-of-truth runtime
- Tailwind is the shared styling layer
- `base_user.html` and `base_admin.html` are the documented layout contracts
- requirements, architecture, API, and infrastructure docs describe the same stack

### Track 2. Customer storefront and account flows

Goal:

- menu-first storefront rendered by Django templates
- product browsing, category filtering, cart, checkout, addresses, order history

Implementation approach:

- use `base_user.html` for storefront, account, cart, checkout, and order pages
- keep page-specific content in child templates only
- use Django forms for account, address, checkout, and review interactions
- reserve selective JSON endpoints for cart updates, checkout recalculation, and live order status refresh

### Track 3. Admin and operations portal

Goal:

- custom staff/admin experience with its own shell, not just stock Django admin
- catalog management, order operations, delivery workflows, refunds, reporting, and notifications

Implementation approach:

- use `base_admin.html` for `/dashboard/*` style routes
- include sidebar navigation, utility header, breadcrumbs, action slots, and dense data views
- enforce role-aware page visibility using Django groups and permissions
- use tables, filters, and multi-step operational forms within the admin shell

### Track 4. Layout and design system

Goal:

- create a durable Tailwind-powered template system that prevents duplicated page chrome

Implementation approach:

- `templates/base_user.html` owns marketing header, footer, cart access, and storefront framing
- `templates/base_admin.html` owns sidebar nav, top utility bar, breadcrumbs, and admin actions
- shared partials should cover header, footer, sidebar, alerts, breadcrumbs, and page title blocks
- page templates must extend one base template and fill named blocks only
- Tailwind config should hold shared tokens for color, spacing, typography, container widths, and breakpoints

### Track 5. Django application boundaries

Goal:

- organize the codebase by business capability while preserving a single deployable web platform

Recommended app structure:

- `accounts` for authentication, profiles, groups, permissions, addresses
- `catalog` for categories, products, variants, merchandising
- `orders` for cart, checkout, orders, milestones, reviews
- `payments` for Stripe integration, refunds, reconciliation
- `delivery` for zones, assignments, ETA, POD, delivery states
- `notifications` for templates, broadcasts, and email workflows
- `reporting` for dashboards, exports, invoices, receipts, analytics aggregation

### Track 6. Background workflows

Goal:

- keep request/response flows fast while pushing slow or scheduled work to Celery

Implementation approach:

- use Celery for notification dispatch, payment reconciliation, report generation, retry workflows, and daily resets
- keep PostgreSQL as the source of truth for all business state transitions
- use Redis for cache and coordination only

## Frontend Template Contract

### User layout

Template: `templates/base_user.html`

Responsibilities:

- public navigation and brand presentation
- category and menu browsing shell
- account links and cart access
- softer visual treatment than staff tools
- responsive layout for landing, listing, detail, checkout, and account pages

Expected blocks:

- `title`
- `hero`
- `page_actions`
- `content`
- `footer_extras`

### Admin layout

Template: `templates/base_admin.html`

Responsibilities:

- sidebar navigation
- top utility bar
- breadcrumbs
- primary page actions
- dense forms, tables, status chips, and dashboard widgets
- permission-aware navigation for staff/admin roles

Expected blocks:

- `title`
- `breadcrumbs`
- `primary_actions`
- `sidebar`
- `content`
- `admin_scripts`

## Working Principles

- prefer Django views, forms, and templates for primary product flows
- keep JSON endpoints small and purposeful
- never duplicate full layout chrome in child templates
- document layout ownership whenever a new page type is added
- keep Postgres canonical and treat Redis as supporting infrastructure
- keep third-party integrations behind service interfaces
- keep admin operations in the custom admin shell, not hidden in ad hoc pages

## Near-Term Delivery Checklist

1. Define the Django project structure and app boundaries.
2. Create the documented template inheritance model for `base_user.html` and `base_admin.html`.
3. Standardize Tailwind tokens and responsive layout rules.
4. Map customer routes to the user layout and staff/admin routes to the admin layout.
5. Replace legacy auth assumptions with Django sessions, groups, and permissions.
6. Document which interactions remain JSON endpoints versus standard Django form posts.
7. Keep Celery, Redis, object storage, and PostgreSQL responsibilities explicit in every implementation area.
