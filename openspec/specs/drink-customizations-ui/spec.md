# drink-customizations-ui

## Purpose

Let customers select drink customizations, see active-tier subtotals, submit extras, and retain or reset selections at the appropriate time.

## Requirements

### Requirement: Customization checkboxes on menu cards

Each menu card SHALL display a set of checkboxes for available customization options. Options SHALL be loaded from `GET /api/customizations`. Each checkbox SHALL show the option name and surcharge price (e.g., "Extra Espresso Shot +$0.75").

#### Scenario: Menu card displays customization options
- **WHEN** the menu loads
- **THEN** each menu card SHALL show checkboxes for all available customizations with their names and prices

#### Scenario: Checkboxes are unchecked by default
- **WHEN** a menu card is rendered
- **THEN** all customization checkboxes SHALL be unchecked

### Requirement: Dynamic price update

The order button subtotal SHALL update as customization checkboxes, size, or effective time changes. It SHALL equal the selected size's effective tier price plus all checked full-price surcharges. Time-only updates SHALL preserve selected sizes and checked customizations.

#### Scenario: Checking a customization updates the price
- **WHEN** Extra Espresso Shot is checked on a medium latte with Peak base $5.50
- **THEN** the button SHALL show $6.25

#### Scenario: Unchecking a customization updates the price
- **WHEN** Extra Espresso Shot is unchecked on that Peak medium latte
- **THEN** the button SHALL show $5.50

#### Scenario: Changing size recalculates with customizations
- **WHEN** Extra Espresso Shot remains checked while a Peak latte changes from medium to large
- **THEN** the button SHALL show $7.25

#### Scenario: Off-Peak customization changes
- **WHEN** Extra Espresso Shot is checked on an Off-Peak medium latte with effective base $4.40
- **THEN** the button SHALL show $5.15 and unchecking it SHALL restore $4.40

### Requirement: Order submission includes selected customizations

When the order button is clicked, the `POST /api/orders` request SHALL include the IDs of all checked customizations in the `customizations` field.

#### Scenario: Order placed with customizations
- **WHEN** a customer checks "Oat Milk" and "Whipped Cream" then clicks Order
- **THEN** the request body SHALL include `"customizations": ["oat-milk", "whipped-cream"]`

#### Scenario: Order placed without customizations
- **WHEN** a customer clicks Order with no checkboxes checked
- **THEN** the request body SHALL include `"customizations": []`

### Requirement: Customization checkboxes reset after ordering

After successful confirmed order placement, only the ordered card's customization checkboxes SHALL reset to unchecked. Its selected size SHALL remain selected and the displayed price SHALL return to that size's current effective tier base price. Other cards' selections SHALL remain unchanged.

#### Scenario: Checkboxes reset after order
- **WHEN** a Peak order succeeds
- **THEN** the ordered card's checkboxes SHALL clear and its price SHALL show the selected size's Peak base price

#### Scenario: Off-Peak reset retains discount
- **WHEN** an Off-Peak Large Neural Network Latte order with extras succeeds while the menu remains Off-Peak
- **THEN** the ordered card SHALL clear extras and show $5.20 rather than $6.50

### Requirement: Order queue displays customizations

Each order in the order queue SHALL display its customizations. If an order has customizations, they SHALL be visible as part of the order details.

#### Scenario: Order with customizations shown in queue
- **WHEN** an order with customizations is displayed in the order queue
- **THEN** the customization names SHALL be visible in the order details

#### Scenario: Order without customizations shows no extras
- **WHEN** an order with no customizations is displayed in the order queue
- **THEN** no customization detail SHALL be shown
