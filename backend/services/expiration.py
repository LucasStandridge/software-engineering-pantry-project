"""Utilities for classifying inventory expiration dates."""

from datetime import date


def classify_expiration(
    expiration_date: date | None,
    today: date | None = None,
    warning_days: int = 3,
) -> str:
    """Classify an item based on its expiration date."""

    if not isinstance(warning_days, int) or isinstance(warning_days, bool):
        raise ValueError("warning_days must be a non-negative integer")

    if warning_days < 0:
        raise ValueError("warning_days must be a non-negative integer")

    if expiration_date is None:
        return "unknown"

    if not isinstance(expiration_date, date):
        raise TypeError("expiration_date must be a date or None")

    if today is None:
        today = date.today()

    if not isinstance(today, date):
        raise TypeError("today must be a date")

    days_remaining = (expiration_date - today).days

    if days_remaining < 0:
        return "expired"

    if days_remaining <= warning_days:
        return "expiring_soon"

    return "fresh"

def summarize_expiration(items, today=None, warning_days=3):
    """Summarize inventory items by expiration status."""
    counts = {
        "expired": 0,
        "expiring_soon": 0,
        "fresh": 0,
        "unknown": 0,
    }

    for item in items:
        status = classify_expiration(
            item["expiration_date"],
            today=today,
            warning_days=warning_days,
        )
        counts[status] += 1

    return {
        "total": len(items),
        "counts": counts,
    }