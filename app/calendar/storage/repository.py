"""Atomic JSON storage for downloaded calendar events."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.calendar.models.event import CalendarEvent


class EventRepository:
    """Stores the calendar in the versioned local events document."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(__file__).with_name("events.json")

    def load(self) -> list[CalendarEvent]:
        """Return all stored events; an absent store is an empty calendar."""
        if not self.path.exists():
            return []
        document = json.loads(self.path.read_text(encoding="utf-8"))
        if document.get("version") != 1:
            raise ValueError("unsupported calendar storage version")
        return [CalendarEvent.from_dict(item) for item in document["events"]]

    def save(self, events: list[CalendarEvent], source_count: int) -> None:
        """Replace storage atomically after a successful update."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "version": 1,
            "last_updated": datetime.now(UTC).isoformat(),
            "source_count": source_count,
            "event_count": len(events),
            "events": [event.to_dict() for event in sorted(events, key=lambda item: item.scheduled_at)],
        }
        temporary = self.path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)
