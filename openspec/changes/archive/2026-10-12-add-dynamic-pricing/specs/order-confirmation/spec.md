## MODIFIED Requirements

### Requirement: Confirmation overlay shows order summary

The confirmation overlay SHALL display drink name, selected size, original base price, stored quote tier, each selected customization with its full surcharge, and the pre-tax quoted subtotal. Off-Peak quotes SHALL show a negative 20% base-price discount line; Peak quotes SHALL omit it. The customization section SHALL be omitted when none are selected. Opening the overlay SHALL capture the effective HH:MM time and selections used for the quote. Clock or slider changes while it is open SHALL NOT alter the quote. Going back and reopening SHALL obtain the current quote and preserve card selections.

#### Scenario: Order with customizations shows full breakdown
- **WHEN** a Peak Medium Neural Network Latte with base $5.50, Extra Espresso Shot $0.75, and Oat Milk $0.60 is reviewed
- **THEN** the overlay SHALL show drink and size, both customization prices, Peak tier, and subtotal $6.85

#### Scenario: Order without customizations omits customization section
- **WHEN** a Peak Large Deep Learning Doppio without customizations is reviewed
- **THEN** the overlay SHALL show drink and size and its full base subtotal, with no customization lines

#### Scenario: Off-Peak quote shows discount
- **WHEN** a Large Neural Network Latte with extra shot is reviewed at 15:00
- **THEN** the overlay SHALL show original base $6.50, discount -$1.30, extra shot $0.75, Off-Peak tier, and subtotal $5.95

#### Scenario: Boundary crossed while confirmation is open
- **WHEN** a Peak quote is opened at 08:59 and server time reaches 09:00 before confirmation
- **THEN** the overlay SHALL retain its Peak quote and captured time 08:59

#### Scenario: Reopening obtains current quote
- **WHEN** the customer goes back after the clock reaches 09:00 and reopens the overlay in real-time mode
- **THEN** it SHALL use refreshed Off-Peak pricing and preserve selected size and customizations

### Requirement: Confirm button submits the order

The overlay SHALL include Confirm Order. Clicking it SHALL submit POST /api/orders with captured item_id, size, customization IDs, and time, then close the overlay, refresh the order list, and clear the ordered card's customization checkboxes on success. The captured time SHALL be sent in both real-time and simulated modes so the backend calculates the displayed quote. The backend SHALL remain authoritative for all price amounts.

#### Scenario: Confirming submits and closes overlay
- **WHEN** the customer confirms a quote captured at 15:00
- **THEN** the request SHALL include the captured item_id, size, customization IDs, and time 15:00
- **AND** successful submission SHALL close the overlay, refresh orders, and clear the ordered card's customizations

#### Scenario: Later time changes do not alter submission
- **WHEN** the effective menu time changes while a quote is open and the customer confirms
- **THEN** the request SHALL send the quote's captured time rather than the later time