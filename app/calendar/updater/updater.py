"""Download official schedules and persist a deduplicated local calendar."""

from __future__ import annotations

from dataclasses import dataclass

from app.calendar.models.event import CalendarEvent
from app.calendar.official_sources.base import (
    HttpClient,
    OfficialCalendarSource,
    SourceDownloadError,
)
from app.calendar.storage.repository import EventRepository


@dataclass(frozen=True, slots=True)
class UpdateResult:
    """Outcome of a calendar refresh."""

    source_count: int
    event_count: int
    failures: tuple[str, ...]


class CalendarUpdater:
    """Refreshes the local store from explicit official-source adapters."""

    def __init__(self, repository: EventRepository, sources: tuple[OfficialCalendarSource, ...]) -> None:
        self._repository = repository
        self._sources = sources

    def update(self, client: HttpClient | None = None) -> UpdateResult:
        """Persist events only when every configured source downloads successfully."""
        events: dict[str, CalendarEvent] = {}
        failures: list[str] = []
        successful_sources = 0
        for source in self._sources:
            try:
                downloaded = source.fetch(client)
            except (OSError, ValueError, KeyError, SourceDownloadError) as error:
                failures.append(f"{source.name}: {error}")
                continue
            successful_sources += 1
            for event in downloaded:
                events[event.event_id] = event
        if failures:
            return UpdateResult(successful_sources, len(events), tuple(failures))
        self._repository.save(list(events.values()), source_count=successful_sources)
        return UpdateResult(successful_sources, len(events), ())
