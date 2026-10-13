## Context

BeanBotics uses FastAPI services, a vanilla JavaScript frontend, JSON menu data, and in-memory orders. OrderService currently calculates the size price, customization surcharges, tax, and COGS on placement and stores receipt details on each order. The frontend includes size selection, customization controls, a confirmation overlay, completed-order receipts, and a financial dashboard. Dynamic pricing must stay consistent across these surfaces without changing ingredient consumption or order lifecycle rules.

## Goals / Non-Goals

**Goals:**
- Apply Peak or Off-Peak pricing consistently to all drink sizes.
- Discount only the base drink price by 20% during Off-Peak periods.
- Support configurable time windows and per-browser simulated time.
- Preserve quoted pricing through confirmation and stored pricing through order completion.
- Show itemized discounts and pre-tax revenue grouped by stored pricing tier.

**Non-Goals:**
- Authentication, payments, database persistence, or historical reporting.
- Per-drink overrides, customer-specific discounts, coupons, loyalty programs, or multiple discount percentages.
- A customer-facing schedule or configuration editor.

## Decisions

### Backend pricing service and configuration

Introduce a small PricingService responsible for configuration validation, effective time, tier selection, and money calculations. Load backend/data/pricing.json at startup, using timezone UTC and Peak intervals [07:00, 09:00) and [11:30, 13:30) by default. Store interval endpoints as HH:MM; reject malformed, empty, overlapping, reversed, or overnight intervals at startup. Off-Peak covers the complement. Use zoneinfo for a configurable IANA timezone.

This follows the existing JSON/service pattern rather than embedding schedule decisions independently in routes and JavaScript. Overnight intervals are intentionally unsupported in this first version; operators can express overnight Peak periods as two valid intervals ending and starting at midnight using 24:00 exclusively as an interval end.

### Explicit, request-local time contract

GET /api/menu accepts an optional time query parameter. POST /api/orders accepts an optional time string in its JSON body. Both accept exactly HH:MM, 00:00 through 23:59; supplied values are already local to the configured pricing timezone. Invalid request values return HTTP 422. Omitted values use the server clock converted to the configured timezone. Overrides do not mutate shared server state.

Keep GET /api/menu's existing {"items": [...]} response envelope. Add original_price and pricing metadata to each size alongside price, where price is the effective discounted or full base price; preserve all recipe and other existing data. Metadata includes pricing_tier, discount_rate, effective_time, and pricing_timezone. POST and GET order responses expose pricing_tier and stored itemized discount data. Status responses retain the same stored values.

Per-request overrides avoid one customer's slider affecting another customer. The override is deliberately available in this unauthenticated training app, not a secure production discount entitlement. A production deployment would need a trusted simulation boundary before accepting arbitrary customer time overrides.

### Decimal calculation and immutable order snapshot

Use Decimal values constructed from decimal strings and ROUND_HALF_UP to two decimal places. Calculate discount_amount = round(original_price * discount_rate), discounted_base_price = original_price - discount_amount, subtotal = discounted_base_price + sum(customization prices), tax = round(subtotal * 0.085), and total = subtotal + tax. Convert to JSON numeric values at serialization. Peak discount rate and amount are zero.

Keep total_price as the pre-tax subtotal. Keep items_detail.base_price as the original, undiscounted size price and add pricing_tier, discount_rate, discount_amount, and discounted_base_price. Store these alongside effective pricing time when the order is created. Never recalculate a stored order during GET, PATCH, cancellation, configuration changes, or slider movement. Recipe calculations and stored COGS remain unchanged.

Storing original and charged prices avoids reconstructing receipts from a potentially changed menu. Decimal arithmetic avoids platform-dependent binary rounding at half-cent boundaries; it intentionally standardizes receipt rounding rather than relying on Python round.

### Frontend quote and time controls

Default to real-time mode. Display the effective time and a minute-step time slider; moving the slider enables simulated mode. Provide a reset control returning to server time. Refresh menu pricing at least once per minute in real-time mode and on slider changes without reloading the page. Preserve size selections and customization checkboxes. Discard stale responses when requests finish out of order.

Calculate button and overlay subtotals from the effective base price plus unchanged customization surcharges. Opening confirmation snapshots the effective time, tier, selected drink, size, customizations, and quoted subtotal. Confirm sends that captured HH:MM value and the captured selections, not a later slider value. Dismissing and reopening obtains a fresh quote. Prices are not recomputed inside an open overlay. After successful placement, clearing customizations restores the selected size's current effective price, not its original price.

Freezing a short-lived quote avoids silently changing the amount the customer confirmed. This is appropriate to the existing in-memory app; signed quotes, expiry, and production trust enforcement are out of scope.

### Receipts and financial reporting

Receipts label the stored Peak or Off-Peak tier. Off-Peak receipts show the original base line, a negative discount line, full-price customization lines, discounted subtotal, tax, and total. Omit customization lines when none exist and omit discount lines for Peak orders. Keep existing inline receipt controls unchanged.

Dashboard revenue uses total_price, excluding tax. Preserve aggregate revenue, COGS, and gross margin and add Peak and Off-Peak revenue totals and a tier column per order. Tier revenue sums equal aggregate revenue. Use the current non-cancelled order list, including pending, preparing, ready, and completed orders, as today. Cancellation removes the order's revenue and COGS; completion does not. Changing current time never changes existing order rows or totals. Empty and absent-tier totals are $0.00. Negative margins are displayed without clamping.

## Risks / Trade-offs

- Unrestricted simulation can select a discount at any time -> Explicitly limit this design to the training app and require a trust boundary for production.
- Minute polling can leave menu prices briefly stale -> Freeze the displayed quote at confirmation and submit its effective time; replace stale responses only with the newest request.
- Decimal half-up rounding can differ from existing half-even results -> Cover cent-boundary fixtures and document the standardized calculation.
- Full delta replacements can accidentally remove existing scenarios -> Retain unaffected behavior and use baseline capability names for modifications.
- In-memory snapshots disappear on restart -> Preserve the existing no-persistence scope and do not imply historical reporting.

## Migration Plan

1. Normalize the proposal capability inventory and delta specs before implementation.
2. Add configuration and PricingService, then integrate menu responses and order snapshot calculations without changing the menu response envelope or total_price meaning.
3. Update time controls, menu pricing, confirmation, receipts, and the dashboard together.
4. Run focused backend tests and browser workflows for boundaries, discounts, immutable orders, cancellation, and real/simulated time modes.
5. Roll back by reverting the implementation and restarting; existing in-memory orders do not require a data migration.

## Open Questions

No blocking questions remain for the training app. UTC defaults, half-open windows, half-up rounding, per-browser simulation, and quote freezing are explicit planning assumptions that can be revised before implementation. Production override authorization and quote expiry remain outside this change.