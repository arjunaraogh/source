# Add Dynamic Pricing

## Why

BeanBotics currently uses fixed pricing throughout the day regardless of customer demand. Coffee shops commonly offer discounts during slower periods to attract customers while maintaining standard pricing during peak business hours. Introducing dynamic pricing will help increase customer traffic during off-peak hours, improve revenue opportunities, and provide greater flexibility in pricing management.

## What Changes

This change introduces dynamic pricing based on predefined time-of-day pricing tiers.

The system will:

- Support Peak and Off-Peak pricing tiers
- Define configurable time ranges for each pricing tier
- Provide time simulation capabilities for testing and validation
- Display prices according to the active pricing tier
- Calculate order totals using the active pricing tier
- Include pricing tier information on customer receipts
- Update financial dashboard metrics to reflect dynamic pricing activity

## Capabilities

### New Capabilities

- `pricing-tiers`: Configurable time windows, timezone, per-request overrides, and per-browser time simulation.
- `menu-display`: Tier indicators, effective menu API pricing, and live pricing refresh without losing selections.
- `order-pricing`: Backend-authoritative discount calculations, cent rounding, and immutable order pricing snapshots.

### Modified Capabilities

- `drink-size-selection`: Tier-aware size prices, order button totals, and selected-size submission through confirmation.
- `drink-customizations`: Calculate pre-tax totals from the discounted base price plus full-price surcharges.
- `drink-customizations-ui`: Update prices and post-order resets using the active tier while preserving selections.
- `order-confirmation`: Display and freeze the selected pricing quote, then submit its effective time on confirmation.
- `order-receipt`: Return itemized discount metadata and display the stored tier and discount on completed-order receipts.
- `financial-dashboard`: Report pre-tax revenue by stored tier and retain existing COGS, margin, and cancellation behavior.

## Impact

Backend changes affect menu and order routes, request validation, order response fields, and a new pricing service and JSON configuration. Frontend changes affect time controls, menu rendering, button prices, confirmation, receipts, and financial reporting. The menu API retains its {"items": [...]} envelope and total_price remains the pre-tax subtotal. No database, authentication, payment integration, or new frontend framework is introduced. Existing in-memory order lifecycle and ingredient-cost calculations remain unchanged.

## Scope Boundaries

The following items are out of scope for this change:

- Per-drink discount overrides
- Customer-specific pricing or discounts
- Customer-facing pricing schedules
- Historical pricing data retention and reporting
- Different discount percentages for different off-peak periods
- Promotional coupons or marketing campaigns
- Loyalty program integration

## Expected Outcome

BeanBotics will automatically apply standard pricing during peak hours and discounted pricing during off-peak hours. Customers will see the appropriate prices for the current pricing tier, order calculations will reflect the active pricing rules, receipts will indicate the pricing tier used, and financial reports will accurately represent revenue generated under dynamic pricing.