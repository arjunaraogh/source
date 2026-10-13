## 1. Pricing Configuration and Calculation

- [x] 1.1 Add backend/data/pricing.json with the UTC timezone and default Peak windows [07:00, 09:00) and [11:30, 13:30).
- [x] 1.2 Add PricingService using the existing service pattern; validate timezone and non-overlapping, non-empty, non-overnight intervals at startup, permitting 24:00 only as an interval end.
- [x] 1.3 Implement server-clock and request-local HH:MM tier determination with inclusive starts and exclusive ends; reject invalid request times with HTTP 422.
- [x] 1.4 Implement Decimal half-up discount, subtotal, tax, and total calculations while leaving customization prices and recipe COGS unchanged.
- [x] 1.5 Add focused tests for both Peak windows, exact boundaries, midnight, configurable timezone, invalid configuration, invalid overrides, and cent rounding fixtures.

## 2. Menu API and Order Snapshots

- [x] 2.1 Wire PricingService into app services and accept the optional time query on GET /api/menu and time JSON field on POST /api/orders.
- [x] 2.2 Preserve the menu response envelope and existing fields; add original_price, effective price, pricing_tier, discount_rate, effective_time, and pricing_timezone consistently across all sizes.
- [x] 2.3 Extend Order and placement calculations to store tier, effective time, original price, discount rate and amount, discounted base, customization prices, subtotal, tax, and total.
- [x] 2.4 Return stored pricing_tier and expanded items_detail on POST and GET orders and preserve them through status responses; keep total_price as pre-tax subtotal.
- [x] 2.5 Add API/service tests for Peak and Off-Peak orders, no and multiple customizations, missing overrides, independent request times, and backend-authoritative pricing.
- [x] 2.6 Verify later menu/configuration/time changes and status transitions never change stored pricing or COGS and existing customization validation remains intact.

## 3. Time Controls and Menu Pricing

- [x] 3.1 Add a labeled minute-step time slider, current-time display, real/simulated mode state, and reset-to-server-time control using existing frontend styles.
- [x] 3.2 Refresh prices on slider changes and at least once per minute in real-time mode; discard superseded responses and preserve selected sizes and customization checkboxes.
- [x] 3.3 Render the active tier indicator, Peak normal prices, and Off-Peak original strikethrough plus discounted prices for every size.
- [x] 3.4 Update button subtotals on size, customization, and time changes; after successful order placement clear only the ordered card's customizations and restore its current effective base price.
- [x] 3.5 Verify default medium selection, both slider directions, 00:00 and 23:59 slider values, real-time boundary refresh, reset behavior, and out-of-order response handling.

## 4. Confirmation and Receipts

- [x] 4.1 Show quoted tier, original base, any Off-Peak discount, full-price customization lines, and pre-tax subtotal in the existing confirmation overlay.
- [x] 4.2 Snapshot quote time and selections when the overlay opens; confirm with the captured time in both modes, and obtain a fresh quote when dismissed and reopened.
- [x] 4.3 Render completed-order receipts from stored itemized data with tier label, negative Off-Peak discount line, discounted subtotal, half-up tax, and total; preserve inline toggles and omit absent customization lines.
- [x] 4.4 Verify opening confirmation does not submit, crossing a tier boundary preserves the open quote, Go Back preserves selections, and success resets only the ordered card.
- [x] 4.5 Verify Peak and Off-Peak receipts with and without customizations, multiple open receipts, and receipt stability after time changes and completion.

## 5. Financial Dashboard

- [x] 5.1 Keep aggregate pre-tax revenue, COGS, and margin; add Peak and Off-Peak revenue from stored order tiers and ensure their sum equals total revenue.
- [x] 5.2 Add a per-order tier column and display stored pre-tax revenue, COGS, and positive or negative margin without clamping.
- [x] 5.3 Preserve live refresh and cancellation exclusion; retain completed-order financials and prevent slider changes from repricing historical rows.
- [x] 5.4 Verify empty, one-tier, mixed-tier, placement, cancellation, completion, negative-margin, and slider-change cases with exact expected totals.

## 6. Integration and Documentation

- [x] 6.1 Run focused backend regression tests covering size selection, customization validation, order lifecycle, itemized tax, and unchanged ingredient COGS alongside new pricing tests.
- [x] 6.2 Exercise the complete slider-to-confirmation-to-order-to-receipt-to-dashboard workflow in the browser at desktop and mobile sizes; check labels, prices, controls, and layout for regressions.
- [x] 6.3 Document pricing configuration, timezone and interval semantics, time override examples, cent rounding, quote capture, and the training-only security limitation in README.md.
- [x] 6.4 Run openspec validate add-dynamic-pricing --strict --no-interactive and confirm implementation satisfies all delta scenarios before marking tasks complete.