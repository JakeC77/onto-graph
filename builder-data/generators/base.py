"""Shared utilities for all generators."""
import random
import uuid
from datetime import date, timedelta
from typing import Any


def uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


def rand_between(lo: float, hi: float, decimals: int = 2) -> float:
    return round(random.uniform(lo, hi), decimals)


def rand_int(lo: int, hi: int) -> int:
    return random.randint(lo, hi)


def weighted_choice(choices: list, weights: list):
    return random.choices(choices, weights=weights, k=1)[0]


def add_business_days(start: date, days: int) -> date:
    """Advance a date by N business days."""
    current = start
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Mon-Fri
            added += 1
    return current


def date_in_range(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(0, delta)))


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def round_to_cents(value: float) -> float:
    return round(value, 2)


def seasonal_weight(month: int, weights: list[float]) -> float:
    """weights is a 12-element list indexed 0..11 (Jan..Dec)."""
    return weights[month - 1]


def apply_variance(base: float, variance_pct: float = 0.10) -> float:
    """Return base ± variance_pct (uniform)."""
    lo = base * (1 - variance_pct)
    hi = base * (1 + variance_pct)
    return round(random.uniform(lo, hi), 2)


class Registry:
    """Simple lookup store passed between generators."""

    def __init__(self):
        self._store: dict[str, list[dict]] = {}

    def add(self, entity_type: str, record: dict) -> dict:
        self._store.setdefault(entity_type, []).append(record)
        return record

    def all(self, entity_type: str) -> list[dict]:
        return self._store.get(entity_type, [])

    def by_id(self, entity_type: str, id_field: str, id_value: Any) -> dict | None:
        for record in self.all(entity_type):
            if record.get(id_field) == id_value:
                return record
        return None

    def filter(self, entity_type: str, **kwargs) -> list[dict]:
        results = []
        for record in self.all(entity_type):
            if all(record.get(k) == v for k, v in kwargs.items()):
                results.append(record)
        return results

    def to_dict(self) -> dict[str, list[dict]]:
        return dict(self._store)
