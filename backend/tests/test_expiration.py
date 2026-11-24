"""Tests for inventory expiration classification."""

from datetime import date, timedelta

import pytest

from backend.services.expiration import (
    classify_expiration,
    summarize_expiration,
)


@pytest.mark.parametrize(
    "days_remaining, expected_status",
    [
        (-5, "expired"),
        (-1, "expired"),
        (0, "expiring_soon"),
        (1, "expiring_soon"),
        (3, "expiring_soon"),
        (4, "fresh"),
        (30, "fresh"),
    ],
)
def test_expiration_classification(days_remaining, expected_status):
    """Verify expiration statuses at different date boundaries."""
    today = date(2026, 11, 15)
    expiration_date = today + timedelta(days=days_remaining)

    assert classify_expiration(expiration_date, today) == expected_status


def test_missing_expiration_date():
    """Verify items without expiration dates are classified as unknown."""
    assert classify_expiration(None, date(2026, 11, 15)) == "unknown"


def test_custom_warning_window():
    """Verify expiration thresholds can be customized."""
    today = date(2026, 11, 15)
    expiration_date = today + timedelta(days=5)

    assert classify_expiration(expiration_date, today, warning_days=7) == "expiring_soon"
    assert classify_expiration(expiration_date, today, warning_days=3) == "fresh"


@pytest.mark.parametrize("warning_days", [-1, 1.5, True, "3"])
def test_invalid_warning_window(warning_days):
    """Verify invalid warning thresholds are rejected."""
    with pytest.raises(ValueError):
        classify_expiration(date(2026, 11, 20), warning_days=warning_days)


def test_invalid_expiration_date():
    """Verify non-date expiration values are rejected."""
    with pytest.raises(TypeError):
        classify_expiration("2026-11-20", date(2026, 11, 15))

def test_expiration_summary_counts():
    """Verify inventory items are grouped by expiration status."""
    today = date(2026, 11, 19)

    items = [
        {"expiration_date": date(2026, 11, 18)},
        {"expiration_date": date(2026, 11, 20)},
        {"expiration_date": date(2026, 11, 30)},
        {"expiration_date": None},
    ]

    result = summarize_expiration(items, today=today)

    assert result["total"] == 4
    assert result["counts"] == {
        "expired": 1,
        "expiring_soon": 1,
        "fresh": 1,
        "unknown": 1,
    }