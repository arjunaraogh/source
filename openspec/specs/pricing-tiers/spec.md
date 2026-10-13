# pricing-tiers

## Purpose

Define time-based Peak and Off-Peak pricing, browser-local time simulation, request-local overrides, and validated pricing schedules.

## Requirements

### Requirement: Dynamic Pricing Tier Definitions

The system SHALL support two pricing tiers: Peak and Off-Peak.

Peak pricing SHALL apply during the following default time windows in the configured pricing timezone, UTC by default. Starts SHALL be inclusive and ends SHALL be exclusive:

- 07:00 <= time < 09:00
- 11:30 <= time < 13:30

Off-Peak pricing SHALL apply during all other times.

During Off-Peak pricing, the system SHALL apply a 20% discount to the base drink price.

The system MUST NOT apply the Off-Peak discount to drink customization surcharges.

#### Scenario: Peak Pricing Window

Given the current time is 8:00 AM  
When a customer views menu pricing  
Then the system SHALL apply Peak pricing  
And the base drink price SHALL remain unchanged.

#### Scenario: Off-Peak Pricing Window

Given the current time is 3:00 PM  
When a customer views menu pricing  
Then the system SHALL apply Off-Peak pricing  
And the base drink price SHALL be reduced by 20%.

#### Scenario: Customization Surcharge Excluded From Discount

Given Off-Peak pricing is active  
And a customer orders a drink with a customization surcharge  
When the order total is calculated  
Then the base drink price SHALL receive a 20% discount  
And the customization surcharge MUST NOT be discounted.

### Requirement: Time Simulation Control

The user interface SHALL provide a time-of-day slider covering 00:00 through 23:59 in one-minute steps and showing the selected time. The page SHALL start in real-time mode using the server's effective time. Moving the slider SHALL enable simulated mode for that browser only. A reset control SHALL return to real-time mode.

The system SHALL use the selected slider value to determine the active pricing tier.

The menu and pricing information SHALL update immediately when the slider value changes.

#### Scenario: Slider Changes Active Tier

Given the slider is set to 8:00 AM  
When the user changes the slider to 3:00 PM  
Then the system SHALL recalculate the active pricing tier  
And the displayed prices SHALL update immediately.

### Requirement: Pricing Time Override API

GET /api/menu SHALL accept an optional time query parameter. POST /api/orders SHALL accept an optional time field in its JSON body. Both SHALL accept exactly HH:MM from 00:00 through 23:59, interpreted in the configured pricing timezone. Invalid values SHALL return HTTP 422. Overrides SHALL be request-local and MUST NOT change another request's clock.

When provided, the time parameter SHALL override the server time for pricing tier determination.

When the time parameter is not provided, the system SHALL use the current server time converted to the configured pricing timezone.

#### Scenario: API Time Override Provided

Given an API request includes a time parameter of 3:00 PM  
When pricing is calculated  
Then the system SHALL use 3:00 PM to determine the active pricing tier  
And the server time SHALL be ignored.

#### Scenario: API Time Override Not Provided

Given an API request does not include a time parameter  
When pricing is calculated  
Then the system SHALL use the current server time to determine the active pricing tier.

#### Scenario: Invalid override rejected
- **WHEN** a request supplies time as 24:00, 8am, an empty string, null, or a non-string value
- **THEN** the API SHALL return HTTP 422 without placing an order

#### Scenario: Independent browsers
- **WHEN** one browser requests simulated time 15:00 and another sends no override
- **THEN** the first SHALL receive Off-Peak pricing and the second SHALL use server time independently

#### Scenario: Reset simulation
- **WHEN** the customer resets simulated time
- **THEN** the menu SHALL request pricing without an override and resume real-time refresh

### Requirement: Pricing configuration validation

The system SHALL load Peak windows and an IANA pricing timezone from backend/data/pricing.json at startup. Valid windows SHALL use inclusive starts and exclusive ends, with 24:00 permitted only as an end. Windows SHALL NOT overlap or be empty, reversed, or cross midnight. Invalid configuration SHALL produce a startup error identifying the invalid entry. All other times SHALL use the fixed 20% Off-Peak discount.

#### Scenario: Valid configuration changes Peak hours
- **WHEN** a valid configuration sets a Peak window from 08:00 to 10:00 and the app restarts
- **THEN** 09:30 SHALL use Peak pricing and 10:00 SHALL use Off-Peak pricing

#### Scenario: Invalid schedule rejected
- **WHEN** configuration includes overlapping intervals, invalid times, an unknown timezone, or an overnight window
- **THEN** startup SHALL fail with an identifying validation error

#### Scenario: Default interval boundaries
- **WHEN** the effective time is 07:00 or 11:30 with the default configuration
- **THEN** the active tier SHALL be Peak
- **WHEN** the effective time is 06:59, 09:00, 11:29, 13:30, or 00:00
- **THEN** the active tier SHALL be Off-Peak