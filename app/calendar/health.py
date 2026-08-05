"""Read-only health inspection for the economic calendar."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from app.calendar.models.event import CalendarEvent
from app.calendar.official_sources.catalog import default_sources
from app.calendar.scheduler.scheduler import IST
from app.calendar.storage.repository import EventRepository


@dataclass(frozen=True, slots=True)
class CalendarHealth:
    """Operational state reported by the calendar health command."""

    calendar_status: str
    source_status: str
    events_loaded: int
    calendar_age_seconds: int | None
    next_event: str | None
    pending_reminder: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def inspect_calendar(repository: EventRepository | None = None) -> CalendarHealth:
    """Return calendar state without sending messages or downloading data."""
    store = repository or EventRepository()
    events = store.load()
    now = datetime.now(UTC)
    next_event = _next_event(events, now)
    age = _calendar_age(store, now)
    pending = _pending_reminder(events, now)
    return CalendarHealth(
        calendar_status="ok" if store.path.exists() else "missing",
        source_status=", ".join(source.name for source in default_sources()),
        events_loaded=len(events),
        calendar_age_seconds=age,
        next_event=next_event.title if next_event else None,
        pending_reminder=pending.title if pending else None,
    )


def _next_event(events: list[CalendarEvent], now: datetime) -> CalendarEvent | None:
    return next((event for event in sorted(events, key=lambda item: item.scheduled_at) if event.scheduled_at > now), None)


def _pending_reminder(events: list[CalendarEvent], now: datetime) -> CalendarEvent | None:
    lower = now.astimezone(IST).timestamp() + (29 * 60)
    upper = now.astimezone(IST).timestamp() + (31 * 60)
    return next(
        (
            event
            for event in events
            if event.is_major and lower <= event.scheduled_at.timestamp() <= upper
        ),
        None,
    )


def _calendar_age(repository: EventRepository, now: datetime) -> int | None:
    if not repository.path.exists():
        return None
    modified = datetime.fromtimestamp(repository.path.stat().st_mtime, tz=UTC)
    return int((now - modified).total_seconds())
