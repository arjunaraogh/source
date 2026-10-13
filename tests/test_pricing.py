import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from backend.services.pricing import PricingService
from fastapi.testclient import TestClient

from backend.app import app, menu_service, order_service


class PricingServiceTests(unittest.TestCase):
    def setUp(self):
        self.pricing = PricingService()

    def from_config(self, config):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "pricing.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            return PricingService(config_path)

    def test_default_windows_and_boundaries(self):
        for time in ("07:00", "08:00", "08:59", "11:30", "12:00", "13:29"):
            with self.subTest(time=time):
                self.assertEqual(self.pricing.get_context(time)["pricing_tier"], "Peak")
        for time in ("00:00", "06:59", "09:00", "11:29", "13:30", "15:00", "23:59"):
            with self.subTest(time=time):
                self.assertEqual(self.pricing.get_context(time)["pricing_tier"], "Off-Peak")

    def test_invalid_time_values(self):
        for time in ("24:00", "8am", "8:00", "08:60", "", None, 800, True, "08:00\n"):
            with self.subTest(time=time), self.assertRaises(ValueError):
                self.pricing.parse_time(time)

    def test_configurable_windows_and_midnight_end(self):
        pricing = self.from_config({"timezone": "UTC", "peak_windows": [
            {"start": "08:00", "end": "10:00"}, {"start": "23:00", "end": "24:00"}
        ]})
        self.assertEqual(pricing.get_context("09:30")["pricing_tier"], "Peak")
        self.assertEqual(pricing.get_context("10:00")["pricing_tier"], "Off-Peak")
        self.assertEqual(pricing.get_context("23:59")["pricing_tier"], "Peak")
        self.assertEqual(pricing.get_context("00:00")["pricing_tier"], "Off-Peak")

    def test_invalid_configurations(self):
        invalid = [
            {}, [], {"timezone": "Unknown/Zone", "peak_windows": []},
            {"timezone": "UTC", "peak_windows": []},
            {"timezone": "UTC", "peak_windows": [{"start": "08:00", "end": "08:00"}]},
            {"timezone": "UTC", "peak_windows": [{"start": "23:00", "end": "02:00"}]},
            {"timezone": "UTC", "peak_windows": [{"start": "24:00", "end": "24:00"}]},
            {"timezone": "UTC", "peak_windows": [{"start": "8am", "end": "09:00"}]},
            {"timezone": "UTC", "peak_windows": [{"start": "08:00"}]},
            {"timezone": "UTC", "peak_windows": [None]},
            {"timezone": "UTC", "peak_windows": [
                {"start": "07:00", "end": "09:00"}, {"start": "08:00", "end": "10:00"}
            ]},
        ]
        for config in invalid:
            with self.subTest(config=config), self.assertRaises(ValueError):
                self.from_config(config)

    def test_server_clock_uses_configured_timezone(self):
        pricing = self.from_config({"timezone": "America/New_York", "peak_windows": [
            {"start": "07:00", "end": "09:00"}
        ]})
        instant = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)
        with patch("backend.services.pricing.datetime") as clock:
            clock.now.side_effect = lambda zone: instant.astimezone(zone)
            context = pricing.get_context()
        self.assertEqual(context["effective_time"], "08:00")
        self.assertEqual(context["pricing_timezone"], "America/New_York")
        self.assertEqual(context["pricing_tier"], "Peak")

    def test_override_is_request_local(self):
        self.assertEqual(self.pricing.get_context("15:00")["pricing_tier"], "Off-Peak")
        self.assertEqual(self.pricing.get_context("08:00")["pricing_tier"], "Peak")

    def test_peak_and_off_peak_surcharges(self):
        peak = self.pricing.calculate_price(6.50, [0.75], self.pricing.get_context("08:00"))
        off_peak = self.pricing.calculate_price(6.50, [0.75], self.pricing.get_context("15:00"))
        self.assertEqual(peak["subtotal"], 7.25)
        self.assertEqual(peak["discount_amount"], 0)
        self.assertEqual(off_peak["discount_amount"], 1.30)
        self.assertEqual(off_peak["discounted_base_price"], 5.20)
        self.assertEqual(off_peak["subtotal"], 5.95)
        self.assertEqual(off_peak["tax"], 0.51)
        self.assertEqual(off_peak["total"], 6.46)

    def test_half_up_tax_and_fractional_discount(self):
        context = self.pricing.get_context("15:00")
        detail = self.pricing.calculate_price(5.00, [1.00], context)
        self.assertEqual((detail["subtotal"], detail["tax"], detail["total"]), (5.00, 0.43, 5.43))
        detail = self.pricing.calculate_price(4.99, [], context)
        self.assertEqual(detail["discount_amount"], 1.00)
        self.assertEqual((detail["subtotal"], detail["tax"], detail["total"]), (3.99, 0.34, 4.33))


class PricingApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        order_service.orders.clear()
        order_service._next_id = 1

    def place_order(self, time="15:00", customizations=None, **extra):
        request = {"item_id": "neural-latte", "size": "large", **extra}
        if time is not None:
            request["time"] = time
        if customizations is not None:
            request["customizations"] = customizations
        response = self.client.post("/api/orders", json=request)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["order"]

    def test_menu_envelope_and_source_prices_preserved(self):
        peak = self.client.get("/api/menu", params={"time": "08:00"}).json()["items"]
        off_peak = self.client.get("/api/menu", params={"time": "15:00"}).json()["items"]
        self.assertEqual(len(peak), len(off_peak))
        for peak_item, off_peak_item in zip(peak, off_peak):
            for size_name, size in peak_item["sizes"].items():
                discounted = off_peak_item["sizes"][size_name]
                self.assertEqual(discounted["original_price"], size["price"])
                self.assertEqual(discounted["recipe"], size["recipe"])
                self.assertEqual(discounted["pricing_tier"], "Off-Peak")
                self.assertEqual(discounted["effective_time"], "15:00")
                self.assertEqual(discounted["pricing_timezone"], "UTC")
        self.assertEqual(off_peak[0]["sizes"]["large"]["price"], 5.20)
        self.assertEqual(menu_service.items[0].sizes["large"]["price"], 6.50)
        self.assertEqual(self.client.get("/api/menu", params={"time": "08:00"}).json()["items"], peak)

    def test_peak_and_off_peak_order_detail_and_unchanged_cogs(self):
        peak = self.place_order("08:00", ["extra-shot"])
        off_peak = self.place_order("15:00", ["extra-shot"])
        self.assertEqual(peak["total_price"], 7.25)
        self.assertEqual(off_peak["total_price"], 5.95)
        self.assertEqual(off_peak["items_detail"]["base_price"], 6.50)
        self.assertEqual(off_peak["items_detail"]["discount_amount"], 1.30)
        self.assertEqual(off_peak["items_detail"]["customizations"][0]["price"], 0.75)
        self.assertEqual(off_peak["items_detail"]["total"], 6.46)
        self.assertEqual(peak["cogs"], off_peak["cogs"])

    def test_no_and_multiple_customizations(self):
        order = self.place_order()
        self.assertEqual(order["customizations"], [])
        self.assertEqual(order["total_price"], 5.20)
        self.assertEqual(order["items_detail"]["total"], 5.64)
        order = self.place_order(customizations=["extra-shot", "oat-milk", "whipped-cream"])
        self.assertEqual(order["total_price"], 7.05)
        self.assertEqual(len(order["items_detail"]["customizations"]), 3)

    def test_missing_override_uses_server_clock_independently(self):
        with patch("backend.services.pricing.datetime") as clock:
            clock.now.return_value = datetime(2026, 10, 12, 8, 0, tzinfo=timezone.utc)
            self.assertEqual(self.place_order()["pricing_tier"], "Off-Peak")
            order = self.place_order(time=None)
            menu = self.client.get("/api/menu").json()["items"]
        self.assertEqual(order["pricing_tier"], "Peak")
        self.assertEqual(menu[0]["sizes"]["medium"]["effective_time"], "08:00")

    def test_invalid_time_returns_422_without_order(self):
        for value in ("24:00", "8am", "", None, 800, True, "08:00\n"):
            with self.subTest(value=value):
                response = self.client.post("/api/orders", json={
                    "item_id": "neural-latte", "size": "large", "time": value
                })
                self.assertEqual(response.status_code, 422)
        for value in ("24:00", "8am", "", "null", "08:00\n"):
            self.assertEqual(self.client.get("/api/menu", params={"time": value}).status_code, 422)
        self.assertEqual(order_service.orders, [])

    def test_client_prices_and_tier_are_ignored(self):
        order = self.place_order(price=0, total_price=0, pricing_tier="Peak", discount_amount=6.50)
        self.assertEqual(order["total_price"], 5.20)
        self.assertEqual(order["pricing_tier"], "Off-Peak")

    def test_snapshot_survives_source_changes_and_status_transitions(self):
        order = self.place_order("08:59", ["extra-shot", "oat-milk"])
        original_price = menu_service.items[0].sizes["large"]["price"]
        original_windows = order_service.pricing_service.peak_windows
        try:
            menu_service.items[0].sizes["large"]["price"] = 50
            order_service.pricing_service.peak_windows = [(0, 1440)]
            for status in ("preparing", "ready", "completed"):
                response = self.client.patch(f"/api/orders/{order['order_id']}", json={"status": status})
                self.assertEqual(response.status_code, 200)
                updated = response.json()["order"]
                for key in ("items_detail", "total_price", "cogs", "pricing_tier", "effective_time"):
                    self.assertEqual(updated[key], order[key])
            listed = self.client.get("/api/orders").json()["orders"][0]
            self.assertEqual(listed["items_detail"], order["items_detail"])
        finally:
            menu_service.items[0].sizes["large"]["price"] = original_price
            order_service.pricing_service.peak_windows = original_windows

    def test_existing_size_customization_and_lifecycle_validation(self):
        for extra in ({"size": "huge"}, {"item_id": "missing"}, {"customizations": ["unknown"]}):
            response = self.client.post("/api/orders", json={
                "item_id": "neural-latte", "size": "large", "time": "08:00", **extra
            })
            self.assertEqual(response.status_code, 400)
        order = self.place_order()
        self.assertEqual(order["status"], "pending")
        self.assertEqual(self.client.patch(f"/api/orders/{order['order_id']}", json={"status": "completed"}).status_code, 400)
        self.assertEqual(self.client.patch("/api/orders/999", json={"status": "preparing"}).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/orders/{order['order_id']}").status_code, 200)
        self.assertEqual(self.client.get("/api/orders").json()["orders"], [])

    def test_existing_receipt_fixtures(self):
        response = self.client.post("/api/orders", json={
            "item_id": "neural-latte", "size": "medium", "time": "08:00",
            "customizations": ["extra-shot", "oat-milk"]
        })
        detail = response.json()["order"]["items_detail"]
        self.assertEqual((detail["subtotal"], detail["tax"], detail["total"]), (6.85, 0.58, 7.43))
        response = self.client.post("/api/orders", json={
            "item_id": "gan-cappuccino", "size": "small", "time": "08:00"
        })
        detail = response.json()["order"]["items_detail"]
        self.assertEqual((detail["subtotal"], detail["tax"], detail["total"]), (4.25, 0.36, 4.61))

    def test_dashboard_empty_and_single_tier(self):
        empty = self.client.get("/api/financials").json()
        for field in ("total_revenue", "peak_revenue", "off_peak_revenue", "total_cogs", "margin"):
            self.assertEqual(empty[field], 0)
        self.assertEqual(empty["orders"], [])
        order = self.place_order("08:00")
        data = self.client.get("/api/financials").json()
        self.assertEqual(data["peak_revenue"], 6.50)
        self.assertEqual(data["off_peak_revenue"], 0)
        self.assertEqual(data["total_revenue"], order["total_price"])
        self.assertNotEqual(data["total_revenue"], order["items_detail"]["total"])

    def test_dashboard_mixed_tiers_and_cancellation(self):
        peak = self.place_order("08:00")
        off_peak = self.place_order("15:00", ["extra-shot"])
        data = self.client.get("/api/financials").json()
        self.assertEqual((data["total_revenue"], data["peak_revenue"], data["off_peak_revenue"]), (12.45, 6.50, 5.95))
        self.assertEqual(data["total_cogs"], round(peak["cogs"] + off_peak["cogs"], 2))
        self.assertEqual(data["orders"][0]["pricing_tier"], "Peak")
        self.assertEqual(data["orders"][1]["pricing_tier"], "Off-Peak")
        self.client.delete(f"/api/orders/{off_peak['order_id']}")
        remaining = self.client.get("/api/financials").json()
        self.assertEqual((remaining["total_revenue"], remaining["off_peak_revenue"]), (6.50, 0))
        self.assertEqual(remaining["total_cogs"], peak["cogs"])
        self.assertEqual(len(remaining["orders"]), 1)

    def test_dashboard_completion_and_time_changes_preserve_financials(self):
        order = self.place_order()
        before = self.client.get("/api/financials").json()
        for status in ("preparing", "ready", "completed"):
            self.client.patch(f"/api/orders/{order['order_id']}", json={"status": status})
        self.client.get("/api/menu", params={"time": "08:00"})
        self.assertEqual(self.client.get("/api/financials").json(), before)

    def test_dashboard_same_drink_cogs_and_negative_margin(self):
        peak = self.place_order("08:00")
        off_peak = self.place_order("15:00")
        rows = self.client.get("/api/financials").json()["orders"]
        self.assertEqual(peak["cogs"], off_peak["cogs"])
        self.assertLess(rows[1]["margin"], rows[0]["margin"])
        order_service.orders.clear()
        self.place_order()
        order_service.orders[0].total_price = 1.00
        order_service.orders[0].cogs = 1.50
        data = self.client.get("/api/financials").json()
        self.assertEqual(data["margin"], -0.50)
        self.assertEqual(data["orders"][0]["margin"], -0.50)