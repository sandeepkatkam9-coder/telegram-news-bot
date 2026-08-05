"""Domain model for economic calendar events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class ImpactLevel(StrEnum):
    """Supported economic-event importance levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True, slots=True)
class CalendarEvent:
    """An economic event obtained from an official publisher."""

    event_id: str
    country: str
    title: str
    scheduled_at: datetime
    markets: tuple[str, ...]
    expected_volatility: str
    source: str
    source_url: str
    impact: ImpactLevel = ImpactLevel.HIGH
    actual: str | None = None
    previous: str | None = None
    forecast: str | None = None
    release_url: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id is required")
        if self.scheduled_at.tzinfo is None:
            raise ValueError("scheduled_at must be timezone-aware")
        if not self.country.strip() or not self.title.strip():
            raise ValueError("country and title are required")
        if not self.markets:
            raise ValueError("at least one affected market is required")

    @property
    def is_major(self) -> bool:
        """Whether the event warrants AutoTrade-HUB notifications."""
        return self.impact is ImpactLevel.HIGH

    def to_dict(self) -> dict[str, object]:
        """Serialize the event without leaking Python-specific types."""
        return {
            "id": self.event_id,
            "country": self.country,
            "title": self.title,
            "scheduled_at": self.scheduled_at.isoformat(),
            "markets": list(self.markets),
            "expected_volatility": self.expected_volatility,
            "source": self.source,
            "source_url": self.source_url,
            "impact": self.impact.value,
            "actual": self.actual,
            "previous": self.previous,
            "forecast": self.forecast,
            "release_url": self.release_url,
        }

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "CalendarEvent":
        """Create an event from the local JSON representation."""
        return cls(
            event_id=str(value["id"]),
            country=str(value["country"]),
            title=str(value["title"]),
            scheduled_at=datetime.fromisoformat(str(value["scheduled_at"])),
            markets=tuple(str(item) for item in value["markets"]),
            expected_volatility=str(value["expected_volatility"]),
            source=str(value["source"]),
            source_url=str(value["source_url"]),
            impact=ImpactLevel(str(value.get("impact", ImpactLevel.HIGH.value))),
            actual=_optional_text(value.get("actual")),
            previous=_optional_text(value.get("previous")),
            forecast=_optional_text(value.get("forecast")),
            release_url=_optional_text(value.get("release_url")),
        )


def _optional_text(value: object) -> str | None:
    return None if value is None else str(value)
