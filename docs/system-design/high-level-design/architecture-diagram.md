# Architecture Diagram

## Overview

This document describes the shipped application architecture for the restaurant-focused Order Management System. The implementation is built around a single FastAPI backend, a Next.js web application, and a Flutter mobile application. Cloud vendors remain optional deployment targets and provider integrations, not the source of truth for runtime design.

## Solution Architecture

```mermaid
graph TB
    subgraph Clients["Client Applications"]
        Web["Next.js Web App<br/>customer + admin/ops"]
        Mobile["Flutter Mobile App<br/>customer-first flows"]
    end

    subgraph API["Application Layer"]
        FastAPI["FastAPI Backend<br/>/api/v1"]
        WS["WebSocket / notifications"]
        Celery["Celery Workers<br/>async jobs"]
    end

    subgraph Domain["OMS Modules"]
        IAM["IAM / Auth / RBAC"]
        Catalog["Catalog<br/>categories · products · variants"]
        Commerce["Commerce<br/>cart · addresses · checkout · coupons"]
        Orders["Orders<br/>state machine · milestones · idempotency"]
        Ops["Operations<br/>warehouses · fulfillment · deliveries · returns"]
        Analytics["Analytics Abstraction<br/>provider-agnostic events"]
        Comms["Communications<br/>email · sms · push"]
    end

    subgraph Data["Core Data"]
        PG[("PostgreSQL<br/>canonical business data")]
        Redis[("Redis<br/>cache · idempotency · hot-path state")]
        ObjectStore[("Local / S3-compatible storage<br/>images · POD · exports")]
    end

    subgraph Providers["Optional Providers"]
        Payments["Payments<br/>Stripe · Khalti · eSewa · PayPal · COD"]
        Notify["Notifications<br/>SMTP · Resend · SES · Twilio · FCM"]
        AnalyticsProviders["Analytics<br/>PostHog · Mixpanel · future adapters"]
        Maps["Maps / geocoding"]
    end

    Web --> FastAPI
    Web --> WS
    Mobile --> FastAPI
    Mobile --> WS

    FastAPI --> IAM
    FastAPI --> Catalog
    FastAPI --> Commerce
    FastAPI --> Orders
    FastAPI --> Ops
    FastAPI --> Analytics
    FastAPI --> Comms

    Catalog --> PG
    Commerce --> PG
    Orders --> PG
    Ops --> PG
    IAM --> PG

    Commerce --> Redis
    Orders --> Redis
    Ops --> Redis

    Ops --> ObjectStore
    Orders --> Celery
    Ops --> Celery
    Comms --> Celery

    Orders --> Payments
    Comms --> Notify
    Analytics --> AnalyticsProviders
    Ops --> Maps
```

## Module Responsibilities

| Module | Runtime | Responsibilities |
|---|---|---|
| Web App | Next.js | Restaurant storefront, customer account flows, admin and operations dashboards |
| Mobile App | Flutter | Customer menu browsing, cart, checkout, orders, profile, addresses |
| FastAPI Backend | Python / FastAPI | Public API, OMS domain logic, auth, RBAC, validation, orchestration |
| Celery Workers | Python / Celery | Reservation expiry, notifications, exports, reconciliation, deferred operations |
| PostgreSQL | SQLModel / PostgreSQL | System of record for customers, catalog, orders, fulfillment, delivery, returns |
| Redis | Redis | Idempotency keys, lightweight coordination, cached hot-path data |
| Object Storage | Local or S3-compatible | Product images, proof-of-delivery artifacts, generated exports |

## Cross-Cutting Concerns

| Concern | Implementation |
|---|---|
| Authentication | FastAPI JWT/session model with existing auth module and optional OTP/social login |
| Authorization | Role-based access enforced in FastAPI and reflected in web/mobile route handling |
| Idempotency | `Idempotency-Key` on OMS mutations, backed by Redis and persisted OMS state |
| State Management | Explicit order, fulfillment, delivery, and return transitions in the OMS service layer |
| Analytics | Provider-agnostic adapter layer for backend, web, and mobile |
| Notifications | Provider abstraction for email, SMS, push, and in-app delivery |
| Storage | Local-first object storage with S3-compatible deployment option |
| Observability | Structured logging, metrics, and analytics/reporting endpoints inside the app stack |
