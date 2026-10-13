# BeanBotics

A coffee ordering web application for BeanBotics Corporation — an AI-powered robotic barista company.

## Setup

1. Create and activate a virtual environment:
   ```bash
   uv venv
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Start the application:
   ```bash
   uv run uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
   ```

4. Open http://localhost:8000 in your browser.

## What It Does

- View the BeanBotics drink menu (5 AI-themed specialty coffees)
- Select small, medium, or large drinks with optional customizations
- View Peak and Off-Peak prices and simulate the pricing time
- Confirm orders before submitting and view completed-order receipts
- View the order queue
- Cancel pending orders
- Compare pre-tax revenue by pricing tier alongside COGS and gross margin

## Dynamic Pricing

Pricing configuration is loaded from `backend/data/pricing.json` at startup:

```json
{
   "timezone": "UTC",
   "peak_windows": [
      {"start": "07:00", "end": "09:00"},
      {"start": "11:30", "end": "13:30"}
   ]
}
```

Peak windows include their start time and exclude their end time. Exactly 09:00 and 13:30 therefore use Off-Peak pricing with this configuration. All other times receive a 20% discount on the base size price only; customization surcharges remain full price. The timezone must be a valid IANA name, such as `UTC` or `America/New_York`. The `tzdata` dependency provides timezone data on Windows.

Restart after changing configuration. Empty, malformed, overlapping, reversed, or overnight windows cause an identifying startup error. `24:00` is allowed only as a window end. Express an overnight Peak period as separate windows ending at 24:00 and beginning at 00:00.

The page starts with server time converted to the configured timezone and refreshes prices every minute. Moving the minute-step slider enables browser-local simulation; **Use Server Time** resets it. Refreshes preserve selected sizes and extras.

### API Time Overrides

`GET /api/menu?time=15:00` returns the existing `{"items": [...]}` envelope. Each size includes its effective `price`, `original_price`, `pricing_tier`, `discount_rate`, `effective_time`, and `pricing_timezone`, while retaining recipe data.

An order can specify the same effective time:

```http
POST /api/orders
Content-Type: application/json

{"item_id": "neural-latte", "size": "large", "customizations": ["extra-shot"], "time": "15:00"}
```

Overrides must be strings in exact `HH:MM` format, from 00:00 through 23:59, interpreted in the pricing timezone. Invalid values, including explicit JSON null, return HTTP 422. Omitting the parameter uses server time. Overrides affect only their request, not other customers.

### Calculation and Stored Quotes

Prices use decimal arithmetic with half-up cent rounding. First round the 20% base-price discount, subtract it from the original price, add full-price customizations, then round 8.5% tax on the subtotal and add that tax. A $6.50 Large Neural Network Latte with a $0.75 extra shot at 15:00 has a $1.30 discount, $5.95 subtotal, $0.51 tax, and $6.46 total.

Opening confirmation captures the displayed selections and effective time, even in server-time mode. Confirm sends that captured time; a later clock or slider change does not alter the open quote. Going back and reopening uses refreshed pricing. The backend remains authoritative for price amounts.

Order responses store `pricing_tier`, `effective_time`, and expanded `items_detail` including original `base_price`, `discount_amount`, `discounted_base_price`, subtotal, tax, and total. Stored prices, tier, tax, and COGS do not change with later clock, menu, configuration, or status changes. Receipts show the stored tier and any Off-Peak discount.

`total_price` and dashboard revenue remain pre-tax. Peak and Off-Peak revenue sum to total revenue; COGS is unaffected by discounts. All non-cancelled orders contribute, including completed orders. Cancelled orders are excluded. Orders and their pricing snapshots are in memory and disappear on restart.

**Security limitation:** Time overrides are deliberately unrestricted in this unauthenticated training app. They are not a production discount entitlement. A production deployment must restrict simulation to a trusted boundary and enforce quote authorization and expiry.

## Tests

After installing application dependencies, run the standard-library pricing and API tests with the temporary HTTP client dependency:

```bash
uv run --with httpx python -m unittest discover -s tests -v
```

Tests cover time boundaries, timezone and configuration validation, decimal rounding, API compatibility, immutable snapshots, customization and lifecycle regressions, COGS, and tier financial reporting.

## Tech Stack

- **Backend:** Python with FastAPI
- **Frontend:** HTML, CSS, vanilla JavaScript
- **Data:** JSON files (no database)
