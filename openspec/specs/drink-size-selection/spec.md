# drink-size-selection

## Purpose

Allow customers to select a drink size, review its active-tier price, and submit the selected size with the captured pricing quote.

## Requirements

### Requirement: Menu cards display size options with prices

Each menu card SHALL display all available sizes (small, medium, large) with prices reflecting the active tier. Peak sizes SHALL display the original price normally. Off-Peak sizes SHALL display the original price with a strikethrough beside the effective discounted price. A visible menu indicator SHALL identify the active tier.

#### Scenario: Menu loads with size options visible
- **WHEN** the menu page loads
- **THEN** every card SHALL show small, medium, and large with the correct active-tier price

#### Scenario: Prices match menu data
- **WHEN** Neural Network Latte size options render during Peak time
- **THEN** small SHALL show $4.50, medium $5.50, and large $6.50

#### Scenario: Off-Peak size prices
- **WHEN** Neural Network Latte size options render during Off-Peak time
- **THEN** original prices SHALL be struck through beside small $3.60, medium $4.40, and large $5.20

### Requirement: Customer can select a drink size
The size selector SHALL allow the customer to choose exactly one size per menu card. Medium SHALL be selected by default.

#### Scenario: Default size is medium
- **WHEN** the menu page loads
- **THEN** each menu card has medium pre-selected as the active size

#### Scenario: Selecting a different size
- **WHEN** the customer selects the "Small" size option on a menu card
- **THEN** the small option becomes active, the previously active option is deactivated, and the order button updates to reflect the small size and price

### Requirement: Order button reflects selected size and price

The order button on each menu card SHALL reflect the selected size's active-tier base price plus selected customization surcharges, excluding tax. Size, customization, and time changes SHALL update the displayed subtotal. Existing single-size selection and default-medium behavior SHALL remain unchanged.

#### Scenario: Order button shows selected size
- **WHEN** the customer selects Large Machine Learning Mocha without customizations during Peak time
- **THEN** the button SHALL read "Order - $7.00"

#### Scenario: Order button updates when size changes
- **WHEN** the customer changes size from large to small
- **THEN** the button SHALL show the small active-tier base price plus any selected surcharges

#### Scenario: Time change updates button price
- **WHEN** a Large Neural Network Latte with extra shot selected changes from Peak to Off-Peak
- **THEN** the button subtotal SHALL change from $7.25 to $5.95 without changing selections

### Requirement: Order is placed with the selected size

Clicking Order SHALL open the existing confirmation overlay without submitting. Confirming SHALL send POST /api/orders with the selected item_id, size, customization IDs, and the effective HH:MM time captured for the displayed quote. The backend SHALL determine pricing from that time. The order queue SHALL show the stored pre-tax price and selected-size drink name.

#### Scenario: Placing a small order
- **WHEN** the customer selects Small Deep Learning Doppio during Peak time and confirms
- **THEN** the request SHALL include item_id deep-doppio, size small, and the captured time
- **AND** the queue SHALL show Small Deep Learning Doppio at $3.50

#### Scenario: Placing a large order
- **WHEN** the customer selects Large Transformer Flat White during Peak time and confirms
- **THEN** the request SHALL include item_id transformer-white, size large, and the captured time
- **AND** the queue SHALL show Large Transformer Flat White at $6.75

#### Scenario: Off-Peak size submission
- **WHEN** the customer confirms a Large Neural Network Latte without customizations quoted at 15:00
- **THEN** POST /api/orders SHALL include size large and time 15:00 and the stored subtotal SHALL be $5.20
