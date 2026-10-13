## ADDED Requirements

### Requirement: Tier-based order price calculation

The backend SHALL determine the pricing tier from the request's effective time and use the configured menu size price as the original price. Peak orders SHALL use the full original price. Off-Peak orders SHALL deduct 20% of the original base price. Customization surcharges SHALL NOT be discounted. Client-supplied prices, discount amounts, and tier labels SHALL NOT determine the charge.

#### Scenario: Order placed during peak hours
- **WHEN** the customer places an order for a Large Neural Network Latte ($6.50) at 8:00am (peak)
- **THEN** the backend uses $6.50 as the base price
- **AND** the order total reflects the full base price plus any customization surcharges

#### Scenario: Order placed during off-peak hours
- **WHEN** the customer places an order for a Large Neural Network Latte ($6.50) at 3:00pm (off-peak)
- **THEN** the backend applies a 20% discount to the base price: $6.50 × 0.80 = $5.20
- **AND** the order total reflects $5.20 plus any customization surcharges at full price

#### Scenario: Customization surcharges are not discounted
- **WHEN** the customer places an order at 3:00pm (off-peak) for a Large Neural Network Latte with an extra espresso shot (+$0.75)
- **THEN** the base price is discounted to $5.20 but the extra shot remains $0.75
- **AND** the pre-tax subtotal is $5.95

### Requirement: Immutable pricing snapshot

At placement, each order SHALL store pricing_tier, effective pricing time, original base price, discount rate, discount amount, discounted base price, customization prices, subtotal, tax, and total. POST and GET order responses SHALL expose the stored tier and itemized amounts. Status updates SHALL preserve them. Later clock, slider, configuration, or menu changes MUST NOT reprice an existing order. COGS SHALL remain determined by the unchanged recipe and customization ingredient costs.

#### Scenario: Price is locked at order placement time
- **WHEN** the customer places an order at 8:59am (peak) and the time crosses into off-peak (9:01am) before the order is completed
- **THEN** the order retains the peak price from when it was placed

#### Scenario: Stored snapshot survives later changes
- **WHEN** the slider or pricing configuration changes after an order is placed and the order is fetched or advanced to completed
- **THEN** its tier, prices, discount, tax, total, and COGS SHALL remain unchanged

### Requirement: Deterministic cent rounding

The system SHALL use decimal arithmetic with ROUND_HALF_UP to two decimal places. Discount amount SHALL equal the rounded original base price times the discount rate. Discounted base price SHALL equal original base price minus that discount amount. Subtotal SHALL equal discounted base price plus customization surcharges. Tax SHALL equal the rounded subtotal times 0.085. Total SHALL equal subtotal plus rounded tax. total_price SHALL remain the pre-tax subtotal.

#### Scenario: Half-cent tax rounds up
- **WHEN** an Off-Peak order has original base price $5.00 and customization surcharges totaling $1.00
- **THEN** discount SHALL be $1.00, discounted base SHALL be $4.00, subtotal SHALL be $5.00, tax SHALL be $0.43, and total SHALL be $5.43

#### Scenario: Fractional-cent discount rounds once
- **WHEN** an Off-Peak test fixture has original base price $4.99 and no customizations
- **THEN** discount SHALL be $1.00, discounted base and subtotal SHALL be $3.99, tax SHALL be $0.34, and total SHALL be $4.33

#### Scenario: Forged client pricing is not authoritative
- **WHEN** a client submits a valid item, size, and time together with a claimed price or tier
- **THEN** the backend SHALL calculate the charge from its own menu, customization, and pricing configuration
