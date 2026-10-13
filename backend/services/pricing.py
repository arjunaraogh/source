import json
import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from backend.models import TAX_RATE


class PricingService:
    def __init__(self, config_path: Optional[Path] = None):
        config_path = config_path or Path(__file__).parent.parent / "data" / "pricing.json"
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        if not isinstance(config, dict):
            raise ValueError("Pricing configuration must be an object")
        timezone_name = config.get("timezone")
        if not isinstance(timezone_name, str):
            raise ValueError("Pricing configuration requires an IANA timezone")
        try:
            self.timezone = ZoneInfo(timezone_name)
        except (ZoneInfoNotFoundError, ValueError) as error:
            raise ValueError(f"Invalid pricing timezone: {timezone_name}") from error
        windows = config.get("peak_windows")
        if not isinstance(windows, list) or not windows:
            raise ValueError("Pricing peak_windows must be a non-empty list")
        self.peak_windows: list[tuple[int, int]] = []
        for index, window in enumerate(windows):
            try:
                if not isinstance(window, dict):
                    raise ValueError("window must be an object")
                start = self.parse_time(window.get("start"))
                end = self.parse_time(window.get("end"), allow_end_of_day=True)
                if start >= end:
                    raise ValueError("window must be non-empty and must not cross midnight")
            except ValueError as error:
                raise ValueError(f"Invalid pricing window {index}: {window}: {error}") from error
            self.peak_windows.append((start, end))
        self.peak_windows.sort()
        for previous, current in zip(self.peak_windows, self.peak_windows[1:]):
            if current[0] < previous[1]:
                raise ValueError(f"Overlapping pricing windows: {previous} and {current}")

    @staticmethod
    def parse_time(value: object, allow_end_of_day: bool = False) -> int:
        if allow_end_of_day and value == "24:00":
            return 1440
        if not isinstance(value, str) or re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value) is None:
            raise ValueError("Pricing time must be HH:MM from 00:00 through 23:59")
        hours, minutes = value.split(":")
        return int(hours) * 60 + int(minutes)

    def get_context(self, time: Optional[str] = None) -> dict:
        effective_time = time if time is not None else datetime.now(self.timezone).strftime("%H:%M")
        minute = self.parse_time(effective_time)
        is_peak = any(start <= minute < end for start, end in self.peak_windows)
        return {
            "pricing_tier": "Peak" if is_peak else "Off-Peak",
            "discount_rate": 0.0 if is_peak else 0.20,
            "effective_time": effective_time,
            "pricing_timezone": self.timezone.key,
        }

    def calculate_price(self, base_price: float, customization_prices: list[float], context: dict) -> dict:
        original = Decimal(str(base_price))
        rate = Decimal(str(context["discount_rate"]))
        discount = (original * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        discounted_base = original - discount
        surcharges = sum((Decimal(str(price)) for price in customization_prices), Decimal("0"))
        subtotal = discounted_base + surcharges
        tax = (subtotal * Decimal(str(TAX_RATE))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            **context,
            "base_price": float(original),
            "discount_amount": float(discount),
            "discounted_base_price": float(discounted_base),
            "subtotal": float(subtotal),
            "tax_rate": TAX_RATE,
            "tax": float(tax),
            "total": float(subtotal + tax),
        }