# financial-dashboard

## Purpose

Show non-cancelled orders' stored revenue, COGS, margins, and pricing-tier revenue alongside the order board with live order-list updates.

## Requirements

### Requirement: Aggregate financial metrics display

The frontend SHALL display total revenue as the sum of total_price (pre-tax subtotals), total COGS as the sum of stored order COGS, and gross margin as revenue minus COGS, alongside the order board. It SHALL additionally display Peak revenue and Off-Peak revenue grouped by each order's stored pricing_tier. Tier revenue SHALL sum to total revenue. The metrics SHALL include all non-cancelled orders regardless of active or completed status. Empty totals and tiers with no orders SHALL display $0.00. Tier-level COGS and margin aggregates are not required.

#### Scenario: Dashboard shows totals with orders present
- **WHEN** non-cancelled orders exist
- **THEN** the dashboard SHALL show their pre-tax revenue, COGS, and gross margin

#### Scenario: Dashboard shows zero state
- **WHEN** no non-cancelled orders exist
- **THEN** aggregate and tier revenue, COGS, and margin SHALL display $0.00

#### Scenario: Dashboard distinguishes peak and off-peak revenue
- **WHEN** orders have been placed during both peak and off-peak hours
- **THEN** the dashboard displays total revenue with a breakdown showing peak revenue and off-peak revenue separately

#### Scenario: Off-peak margins are lower than peak margins
- **WHEN** the same drink is ordered during peak and off-peak hours
- **THEN** the off-peak order shows lower revenue but the same COGS
- **AND** the off-peak gross margin is lower than the peak gross margin

#### Scenario: Single tier present
- **WHEN** all orders are Peak
- **THEN** Peak revenue SHALL equal total revenue and Off-Peak revenue SHALL be $0.00

### Requirement: Per-order financial breakdown

The dashboard SHALL include a row for each non-cancelled order showing its ID, drink name, stored pricing tier, revenue (total_price excluding tax), COGS, and margin (revenue minus COGS). Off-Peak revenue SHALL include the discounted base price plus full-price customizations. Negative margins SHALL be displayed without clamping.

#### Scenario: Per-order row displayed
- **WHEN** orders exist
- **THEN** each non-cancelled order SHALL have a row with ID, name, tier, pre-tax revenue, COGS, and margin

#### Scenario: Order with positive margin
- **WHEN** an order has revenue $6.00 and COGS $1.50
- **THEN** its margin SHALL display $4.50

#### Scenario: Per-order row shows pricing tier
- **WHEN** an order was placed during off-peak hours
- **THEN** the per-order row displays "Off-Peak" in the pricing tier column
- **AND** the revenue reflects the discounted base price plus any full-price customization surcharges

#### Scenario: Order with negative margin
- **WHEN** an order has revenue $1.00 and COGS $1.50
- **THEN** its margin SHALL display -$0.50

### Requirement: Live dashboard updates

The financial dashboard SHALL update whenever the order list is refreshed, including placement and status changes. Cancellation SHALL exclude the cancelled order's revenue and COGS from aggregate and tier metrics. Completing an order SHALL retain its financials. Changing current or simulated time SHALL NOT change existing order rows or totals.

#### Scenario: New order updates totals
- **WHEN** a new Off-Peak order is placed
- **THEN** total and Off-Peak revenue and aggregate COGS SHALL include that order

#### Scenario: Dashboard reflects current order list
- **WHEN** an order is cancelled and removed from the active order list
- **THEN** aggregate revenue, COGS, margin, and the matching tier's revenue SHALL exclude it

#### Scenario: Completion and slider changes preserve financials
- **WHEN** an order completes or the time slider crosses a tier boundary
- **THEN** its stored tier and financial values SHALL remain unchanged in the dashboard

### Requirement: Dashboard positioned alongside order board
The financial dashboard SHALL be displayed in the application layout alongside the existing order board, visible without requiring navigation or toggling.

#### Scenario: Dashboard visible on page load
- **WHEN** the page loads
- **THEN** the financial dashboard section is visible alongside the order board
