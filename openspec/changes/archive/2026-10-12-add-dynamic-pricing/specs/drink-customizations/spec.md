## MODIFIED Requirements

### Requirement: Order model includes customizations

The Order model SHALL include a list of selected customization IDs, defaulting to an empty list. With no customizations, total_price SHALL equal the selected size's effective tier price rather than always its original price.

#### Scenario: Order created without customizations
- **WHEN** an order is placed with no customizations specified
- **THEN** its customizations SHALL be empty and total_price SHALL equal its effective tier base price

#### Scenario: Order created with customizations
- **WHEN** an order is placed with extra-shot and oat-milk
- **THEN** its customizations SHALL store both IDs

### Requirement: Price calculation includes customization surcharges

The order total_price SHALL equal the selected size's discounted or full-price base plus all selected customization surcharges, excluding tax. All five existing customization options SHALL retain their configured surcharges. The Off-Peak discount MUST NOT apply to any customization.

#### Scenario: Single customization adds to price
- **WHEN** a Medium Neural Network Latte with original base $5.50 and extra-shot is placed during Peak time
- **THEN** total_price SHALL be $6.25

#### Scenario: Multiple customizations add to price
- **WHEN** a Small Deep Learning Doppio with original base $3.50, extra-shot, whipped-cream, and almond-milk is placed during Peak time
- **THEN** total_price SHALL be $5.35

#### Scenario: No customizations means base price only
- **WHEN** an order has no customizations
- **THEN** total_price SHALL equal the effective tier base price

#### Scenario: Multiple Off-Peak surcharges remain full price
- **WHEN** a Small Deep Learning Doppio is placed at 15:00 with extra-shot, whipped-cream, and almond-milk
- **THEN** its original base $3.50 SHALL become $2.80, surcharges SHALL remain $1.85, and total_price SHALL be $4.65