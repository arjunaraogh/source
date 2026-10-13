# drink-customizations

## Purpose

Define drink customization options, API contracts, display names, and full-price surcharges applied to active-tier base prices.

## Requirements

### Requirement: Customization options constant

The system SHALL define a `CUSTOMIZATIONS` constant mapping option IDs to their display names and prices:
- `extra-shot`: "Extra Espresso Shot", $0.75
- `oat-milk`: "Oat Milk", $0.60
- `almond-milk`: "Almond Milk", $0.60
- `soy-milk`: "Soy Milk", $0.60
- `whipped-cream`: "Whipped Cream", $0.50

All options SHALL be available for all drinks with no per-drink restrictions.

#### Scenario: Options constant is accessible
- **WHEN** the customization options are queried
- **THEN** the system SHALL return all five options with their IDs, names, and prices

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

### Requirement: POST /api/orders accepts customizations

The `POST /api/orders` endpoint SHALL accept an optional `customizations` field in the request body — a list of customization IDs. If omitted, it SHALL default to an empty list.

#### Scenario: Valid customizations accepted
- **WHEN** a POST request includes `{ "item_id": "neural-latte", "size": "medium", "customizations": ["extra-shot"] }`
- **THEN** the system SHALL create the order with the customization and return HTTP 200 with the order including customizations and adjusted total price

#### Scenario: Invalid customization ID rejected
- **WHEN** a POST request includes a customization ID not in the known options (e.g., `"double-whip"`)
- **THEN** the system SHALL return HTTP 400 with an error describing the invalid customization

#### Scenario: No customizations field defaults to empty
- **WHEN** a POST request omits the `customizations` field
- **THEN** the system SHALL create the order with an empty customizations list (backward compatible)

### Requirement: GET /api/customizations endpoint

The system SHALL expose `GET /api/customizations` returning all available customization options with their IDs, display names, and prices.

#### Scenario: Retrieve all customization options
- **WHEN** a GET request is sent to `/api/customizations`
- **THEN** the system SHALL return a JSON response with all five customization options, each including `id`, `name`, and `price`

### Requirement: Order display name includes customizations

The order `items` list SHALL include the drink name followed by customization names for display purposes. Customizations SHALL appear as a parenthetical suffix, e.g., "Medium Neural Network Latte (Extra Espresso Shot, Oat Milk)".

#### Scenario: Display name with customizations
- **WHEN** an order for a medium Neural Network Latte with `["extra-shot", "oat-milk"]` is created
- **THEN** the `items` list SHALL contain `"Medium Neural Network Latte (Extra Espresso Shot, Oat Milk)"`

#### Scenario: Display name without customizations
- **WHEN** an order with no customizations is created
- **THEN** the `items` list SHALL contain the drink name without a parenthetical suffix
