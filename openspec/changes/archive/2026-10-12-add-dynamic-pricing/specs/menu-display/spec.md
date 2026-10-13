## ADDED Requirements

### Requirement: Menu pricing tier indicator

The menu SHALL show "Peak Pricing" during Peak periods and "Off-Peak Pricing - 20% Off" during Off-Peak periods. The indicator SHALL use the same effective time and tier as the displayed prices.

#### Scenario: Menu during peak hours
- **WHEN** the active time is within a peak window (7:00am-9:00am or 11:30am-1:30pm)
- **THEN** each size option shows its base price normally with no discount indicators
- **AND** the menu displays a "Peak Pricing" indicator

#### Scenario: Menu during off-peak hours
- **WHEN** the active time is outside all peak windows
- **THEN** each size option shows the original base price with a strikethrough and the discounted price (base price minus 20%) beside it
- **AND** the menu displays an "Off-Peak Pricing — 20% Off" indicator

#### Scenario: Prices update when time changes
- **WHEN** the customer adjusts the time simulation slider from a peak time to an off-peak time
- **THEN** the menu prices update immediately to show strikethrough and discounted prices without a page reload

### Requirement: Menu API exposes effective pricing

GET /api/menu SHALL preserve its {"items": [...]} response envelope and existing menu fields. Each size SHALL include price as the effective base price, original_price as the undiscounted price, pricing_tier as Peak or Off-Peak, discount_rate as 0 or 0.20, effective_time as HH:MM, and pricing_timezone. The backend SHALL calculate these fields from a single effective time per request. Recipe data SHALL remain unchanged.

#### Scenario: Off-Peak menu response
- **WHEN** GET /api/menu?time=15:00 returns a size whose original price is $6.50
- **THEN** price SHALL be 5.20, original_price SHALL be 6.50, pricing_tier SHALL be Off-Peak, and discount_rate SHALL be 0.20
- **AND** effective_time SHALL be 15:00 and the response SHALL retain existing size and recipe fields

### Requirement: Menu refresh preserves selections and current pricing

Pricing refreshes SHALL preserve each card's selected size and customization checkboxes. In real-time mode the frontend SHALL refresh pricing at least once per minute; simulated mode SHALL retain its selected time until changed or reset. The frontend SHALL discard responses superseded by a newer pricing request.

#### Scenario: Reverse tier change
- **WHEN** simulated time changes from 15:00 to 08:00
- **THEN** prices SHALL return to Peak prices without discount indicators and selected sizes and customizations SHALL remain unchanged

#### Scenario: Real clock crosses a boundary
- **WHEN** real-time mode remains open as server time reaches 09:00
- **THEN** the next minute refresh SHALL display Off-Peak pricing without reloading the page

#### Scenario: Out-of-order responses
- **WHEN** an older Peak pricing response arrives after the newest Off-Peak response
- **THEN** the menu SHALL retain the newest Off-Peak prices and indicator