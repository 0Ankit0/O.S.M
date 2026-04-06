# C4 Context and Container Diagrams

## C4 Context Diagram

```mermaid
graph TB
    C["Customer<br/>[Person]<br/>Browses menu, places orders,<br/>tracks delivery, manages account"]
    DS["Delivery Staff<br/>[Person]<br/>Updates delivery status,<br/>captures proof of delivery"]
    OM["Operations Manager<br/>[Person]<br/>Manages zones, assignments,<br/>and order operations"]
    AD["Admin<br/>[Person]<br/>Manages catalog, reporting,<br/>configuration, and staff"]

    OMS["Restaurant OMS<br/>[Software System]<br/>Django web platform serving<br/>storefront and admin operations"]

    PG["Stripe<br/>[External System]<br/>Processes payments and refunds"]
    MAIL["Email Provider<br/>[External System]<br/>Sends transactional and custom email"]
    MAPS["Maps Provider<br/>[External System]<br/>ETA, distance, geocoding"]

    C -->|"Storefront, account, checkout [HTTPS]"| OMS
    DS -->|"Delivery updates and POD [HTTPS]"| OMS
    OM -->|"Operations dashboard [HTTPS]"| OMS
    AD -->|"Admin portal [HTTPS]"| OMS
    OMS -->|"Capture and refund requests"| PG
    OMS -->|"Transactional and custom emails"| MAIL
    OMS -->|"ETA and geocoding queries"| MAPS
```

## C4 Container Diagram

```mermaid
graph TB
    subgraph Clients["Client"]
        Browser["Web Browser<br/>[Container]<br/>Customer, staff, and admin pages"]
    end

    subgraph OMS["Restaurant OMS"]
        Proxy["Reverse Proxy<br/>[Container]<br/>TLS termination, routing,<br/>static/media delivery"]
        Django["Django Application<br/>[Container: Python]<br/>Views, forms, templates,<br/>sessions, permissions, domain logic"]
        Workers["Celery Workers<br/>[Container: Python]<br/>Notifications, exports,<br/>retries, reconciliation"]
        Scheduler["Celery Beat<br/>[Container: Python]<br/>Scheduled resets and reports"]
        DB["PostgreSQL<br/>[Container]<br/>Catalog, orders, delivery,<br/>users, reports, templates"]
        Cache["Redis<br/>[Container]<br/>Cache, idempotency support,<br/>short-lived coordination"]
        Storage["Object Storage<br/>[Container]<br/>Images, POD, invoices,<br/>report files"]
    end

    subgraph External["External Systems"]
        Stripe["Stripe"]
        Email["Email Provider"]
        Maps["Maps Provider"]
        Analytics["Analytics Provider"]
    end

    Browser --> Proxy
    Proxy --> Django
    Django --> DB
    Django --> Cache
    Django --> Storage
    Django --> Workers
    Scheduler --> Workers
    Workers --> DB
    Workers --> Cache
    Workers --> Storage
    Django --> Stripe
    Django --> Maps
    Django --> Analytics
    Workers --> Email
```

## Container Responsibilities and Communication

| Container | Runtime | Communication Style | Data Owned |
|---|---|---|---|
| Reverse Proxy | Managed | HTTPS | None |
| Django Application | Python / Django | Synchronous web requests, template rendering, selective JSON endpoints | Business rules and primary request handling |
| Celery Workers | Python / Celery | Async task execution | Deferred workflows and scheduled work |
| Celery Beat | Python / Celery | Scheduled task dispatch | None |
| PostgreSQL | PostgreSQL | ORM and SQL access | Users, catalog, carts, orders, delivery, refunds, reports |
| Redis | Redis | Cache and coordination | Derived or short-lived state only |
| Object Storage | Local or S3-compatible | File reads/writes | Product media, POD artifacts, exports |

## Frontend Container Contract

The Django application exposes two template shells as the primary frontend contract:

- `base_user.html` for storefront and customer account pages
- `base_admin.html` for staff and admin operations pages

Leaf templates extend one of these layouts and fill named blocks for titles, actions, navigation context, and page content. Shared partials provide headers, footers, breadcrumbs, alerts, and sidebar navigation.
