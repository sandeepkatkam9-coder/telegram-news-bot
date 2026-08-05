"""Official-release comparison and notification preparation."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, InvalidOperation

from app.calendar.models.event import CalendarEvent


class ReleaseEngine:
    """Determines a release result from official actual/forecast values."""

    def apply(self, event: CalendarEvent, actual: str, previous: str | None = None) -> tuple[CalendarEvent, str]:
        """Apply published values and classify actual versus forecast."""
        updated = replace(event, actual=actual, previous=previous or event.previous)
        return updated, self.determine_result(actual, event.forecast)

    @staticmethod
    def determine_result(actual: str, forecast: str | None) -> str:
        """Classify the result without making unsupported market-direction claims."""
        if forecast is None:
            return "Official actual published; no consensus forecast available."
        actual_number = _number(actual)
        forecast_number = _number(forecast)
        if actual_number is None or forecast_number is None:
            return "Official actual published; comparison requires manual review."
        if actual_number > forecast_number:
            return "Actual above forecast."
        if actual_number < forecast_number:
            return "Actual below forecast."
        return "Actual in line with forecast."


def _number(value: str) -> Decimal | None:
    cleaned = value.replace(",", "").replace("%", "").strip()
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None
