## MODIFIED Requirements

### Requirement: Backend returns itemized pricing in order responses

The backend SHALL include an `items_detail` object in every order returned by `POST /api/orders` and `GET /api/orders`. The `items_detail` object SHALL contain:
- `base_price`: the original, undiscounted drink price at the selected size
- `pricing_tier`: Peak or Off-Peak, stored at order placement
- `discount_rate`: 0 for Peak or 0.20 for Off-Peak
- `discount_amount`: the rounded discount on base_price only
- `discounted_base_price`: base_price minus discount_amount
- `customizations`: an array of objects, each with `name` and `price`
- `subtotal`: discounted_base_price + sum of customization prices (equal to total_price)
- `tax_rate`: the tax rate applied (0.085)
- `tax`: the tax amount (subtotal times tax_rate, rounded half-up to 2 decimal places)
- `total`: subtotal + tax

The existing `total_price` field SHALL continue to represent the pre-tax subtotal for backward compatibility. The order response SHALL also expose pricing_tier at the order level. All itemized amounts and pricing metadata SHALL be stored at placement and SHALL NOT be recalculated when fetched or when status changes.

#### Scenario: Order with customizations includes itemized detail
- **WHEN** a customer places a Peak order for a Medium Neural Network Latte ($5.50) with Extra Espresso Shot ($0.75) and Oat Milk ($0.60)
- **THEN** the order response SHALL include `items_detail` with:
  - `base_price`: 5.50
  - `pricing_tier`: Peak
  - `discount_rate`: 0
  - `discount_amount`: 0.00
  - `discounted_base_price`: 5.50
  - `customizations`: [{"name": "Extra Espresso Shot", "price": 0.75}, {"name": "Oat Milk", "price": 0.60}]
  - `subtotal`: 6.85
  - `tax_rate`: 0.085
  - `tax`: 0.58
  - `total`: 7.43

#### Scenario: Order without customizations includes itemized detail
- **WHEN** a customer places a Peak order for a Small Generative Adversarial Cappuccino ($4.25) with no customizations
- **THEN** the order response SHALL include `items_detail` with:
  - `base_price`: 4.25
  - `pricing_tier`: Peak
  - `discount_rate`: 0
  - `discount_amount`: 0.00
  - `discounted_base_price`: 4.25
  - `customizations`: []
  - `subtotal`: 4.25
  - `tax_rate`: 0.085
  - `tax`: 0.36
  - `total`: 4.61

#### Scenario: GET /api/orders returns itemized detail for all orders
- **WHEN** `GET /api/orders` is called
- **THEN** every order in the response SHALL include the `items_detail` object

### Requirement: Receipt view for completed orders

Completed orders SHALL display a receipt with a line-item breakdown and a label showing the stored pricing tier. The receipt SHALL use stored order amounts rather than the current menu or slider time. It SHALL show the drink name, size, original base price, each customization on its own line, discounted subtotal, tax labeled "Tax (8.5%)", and visually emphasized tax-inclusive total. Customization lines SHALL be omitted when none exist. Off-Peak receipts SHALL additionally show "Off-Peak Discount (20%)" as a negative amount immediately after the base item. Peak receipts SHALL omit that line. Only the base drink price SHALL be discounted.

#### Scenario: Receipt for order with customizations
- **WHEN** a completed Peak order for Medium Neural Network Latte with original price $5.50, Extra Espresso Shot, and Oat Milk is displayed
- **THEN** the receipt SHALL show:
  - "Neural Network Latte (Medium)" - $5.50
  - "Extra Espresso Shot" — $0.75
  - "Oat Milk" — $0.60
  - Subtotal - $6.85
  - Tax (8.5%) - $0.58
  - Total - $7.43

#### Scenario: Receipt for order without customizations
- **WHEN** a completed Peak order for Small Generative Adversarial Cappuccino with no customizations is displayed
- **THEN** the receipt SHALL show:
  - "Generative Adversarial Cappuccino (Small)" - $4.25
  - Subtotal - $4.25
  - Tax (8.5%) - $0.36
  - Total - $4.61
- **AND** no customization lines SHALL appear

#### Scenario: Receipt for Off-Peak order

- **WHEN** a completed Off-Peak test order has original base price $5.00 and individual customization charges totaling $1.00
- **THEN** the receipt SHALL show base $5.00, discount -$1.00, individual customization lines, subtotal $5.00, tax $0.43, and total $5.43
- **AND** the receipt SHALL label the stored tier Off-Peak

#### Scenario: Receipt for Peak order

- **WHEN** a completed Peak order's receipt is displayed
- **THEN** it SHALL label the tier Peak and omit the discount line while retaining the existing base, customization, subtotal, tax, and total breakdown

#### Scenario: Off-Peak receipt without customizations
- **WHEN** a completed Off-Peak order has original base price $6.50 and no customizations
- **THEN** its receipt SHALL show base $6.50, discount -$1.30, subtotal $5.20, tax $0.44, total $5.64, and no customization lines

#### Scenario: Receipt remains stable across time changes
- **WHEN** an order placed Off-Peak is completed and its receipt opened during Peak time
- **THEN** the receipt SHALL retain the original Off-Peak tier, discount, subtotal, tax, and total