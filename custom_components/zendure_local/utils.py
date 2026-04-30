"""Shared utilities for the Zendure Local integration."""

from collections.abc import Sequence


def detect_percent_scale(data: dict, keys: Sequence[str]) -> int:
    """Infer whether percent-like values are reported as ×1, ×10, or ×100."""
    raw_values = [
        float(v)
        for key in keys
        if (v := data.get(key)) is not None and isinstance(v, (int, float))
    ]
    if any(v > 1000 for v in raw_values):
        return 100
    if any(v > 100 for v in raw_values):
        return 10
    return 1
