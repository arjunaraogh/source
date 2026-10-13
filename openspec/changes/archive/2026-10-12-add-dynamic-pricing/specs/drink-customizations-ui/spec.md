## MODIFIED Requirements

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

### Requirement: Customization checkboxes reset after ordering

After successful confirmed order placement, only the ordered card's customization checkboxes SHALL reset to unchecked. Its selected size SHALL remain selected and the displayed price SHALL return to that size's current effective tier base price. Other cards' selections SHALL remain unchanged.

#### Scenario: Checkboxes reset after order
- **WHEN** a Peak order succeeds
- **THEN** the ordered card's checkboxes SHALL clear and its price SHALL show the selected size's Peak base price

#### Scenario: Off-Peak reset retains discount
- **WHEN** an Off-Peak Large Neural Network Latte order with extras succeeds while the menu remains Off-Peak
- **THEN** the ordered card SHALL clear extras and show $5.20 rather than $6.50