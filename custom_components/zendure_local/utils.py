"""Shared utilities for the Zendure Local integration."""


def detect_percent_scale(data: dict, keys: tuple[str, ...]) -> int:
    """Infer whether percent-like values are reported as ×1, ×10, or ×100."""
    raw_values = [data.get(key) for key in keys if data.get(key) is not None]
    if any(float(v) > 1000 for v in raw_values):
        return 100
    if any(float(v) > 100 for v in raw_values):
        return 10
    return 1
