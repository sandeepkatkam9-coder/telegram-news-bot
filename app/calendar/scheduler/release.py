"""Official-release comparison and notification preparation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from typing import Protocol

from app.calendar.models.event import CalendarEvent


@dataclass(frozen=True, slots=True)
class ReleaseValues:
    """Actual and previous values published by an official source."""

    actual: str | None
    previous: str | None = None


class OfficialReleaseFetcher(Protocol):
    """Source-specific official release reader."""

    def fetch_release(self, event: CalendarEvent) -> ReleaseValues: ...


class ReleaseEngine:
    """Determines a release result from official actual/forecast values."""

    def apply(self, event: CalendarEvent, actual: str, previous: str | None = None) -> tuple[CalendarEvent, str]:
        """Apply published values and classify actual versus forecast."""
        updated = replace(event, actual=actual, previous=previous or event.previous)
        return updated, self.determine_result(actual, event.forecast)

    def fetch_and_apply(
        self,
        event: CalendarEvent,
        fetcher: OfficialReleaseFetcher,
    ) -> tuple[CalendarEvent, str]:
        """Fetch official values, then prepare the release result for Telegram."""
        values = fetcher.fetch_release(event)
        if values.actual is None:
            raise ValueError(f"Official actual value unavailable for {event.event_id}")
        return self.apply(event, values.actual, values.previous)

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
