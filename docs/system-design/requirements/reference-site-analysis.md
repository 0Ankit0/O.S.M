# Reference Site Analysis

## Source

Primary customer-facing reference site:

- https://www.sushiandmore-ue.de/

This site should be treated as the behavioral reference for the replacement OMS storefront and ordering experience, with the new implementation preserving the useful customer journey while improving structure, maintainability, and operational depth.

## Observed Customer Experience

The current site behaves primarily as a menu-first restaurant storefront with a lightweight ordering entry point:

- Immediate hero section with restaurant name and a clear "Online bestellen" call to action.
- "Beliebte Produkte" section near the top to highlight popular items before the full menu.
- Strong category-led browsing rather than search-led browsing.
- Menu categories surfaced prominently:
  - `Mittag`
  - `Starters`
  - `Sushi`
  - `Gerichte`
  - `Extras`
  - `Getränke`
  - `Dessert`
- Deep nested product presentation inside categories and subgroups such as:
  - `Maki`
  - `Nigiri`
  - `Inside out Roll`
  - `Special Topping Roll`
  - `Futo Roll`
  - `Tempura Roll`
  - `Rocket Roll`
  - `Sashimi`
  - `Bento Box`
- Each item is shown with:
  - product name
  - unit/portion count
  - price
  - short ingredient or preparation description
- Contact and location are visible on the same page:
  - business name
  - street address
  - phone number
- The site appears optimized around fast menu discovery and quick transition into ordering rather than a content-heavy marketing site.

## Functional Implications For The Replacement OMS

The new implementation should preserve these storefront behaviors:

- Menu-first landing experience with a clear primary order CTA.
- Featured or popular products near the top of the storefront.
- Strong category navigation that mirrors how customers mentally browse food items.
- Product cards with concise descriptions, visible prices, and quick add-to-cart actions.
- Restaurant identity and trust details visible without forcing users deep into navigation.

The new OMS should improve on the reference by adding:

- real cart and checkout ownership inside the platform
- structured order history and milestone tracking
- address handling and serviceability checks
- authenticated customer flows
- richer operations support for fulfillment, delivery, returns, and analytics
- cleaner admin-side product/category/inventory management

## Storefront Mapping Into OMS

Reference site concept -> OMS replacement behavior:

- Hero + order CTA -> customer storefront landing with direct `Shop` and `Cart` entry points
- Beliebte Produkte -> featured products / popular items section
- Static menu categories -> database-backed categories and subcategories
- Menu item list -> product + variant catalog
- Ingredient text -> product descriptions and specifications
- Contact block -> storefront footer/header contact and location module
- External order step -> internal cart, checkout, and order creation APIs

## UX Guidance

When implementing or refining the storefront, use the reference site as the baseline for:

- information density
- menu category structure
- product naming style
- concise item descriptions
- visible pricing
- quick path from browsing to ordering

Do not copy the old site literally. The goal is to preserve the familiar user journey while upgrading the experience into a modern OMS-backed product.
