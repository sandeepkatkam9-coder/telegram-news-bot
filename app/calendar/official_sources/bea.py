"""Official Bureau of Economic Analysis release-calendar adapter."""

from __future__ import annotations

import re
from datetime import datetime
from html import unescape
from typing import Protocol
from zoneinfo import ZoneInfo

from app.calendar.models.event import CalendarEvent, ImpactLevel
from app.calendar.official_sources.base import SourceDownloadError
from app.calendar.official_sources.bls import UrlLibTextClient

BEA_SCHEDULE_URL = "https://www.bea.gov/news/schedule"
EASTERN = ZoneInfo("America/New_York")


class TextClient(Protocol):
    """Text client contract used by the source and tests."""

    def get_text(self, url: str, *, timeout: float) -> str: ...


class BeaSource:
    """Downloads BEA's official schedule for GDP and PCE releases."""

    name = "BEA"

    def fetch(self, client: TextClient | None = None) -> list[CalendarEvent]:
        """Return supported high-impact BEA releases from the official schedule."""
        try:
            html = (client or UrlLibTextClient()).get_text(BEA_SCHEDULE_URL, timeout=20.0)
        except (OSError, TimeoutError, SourceDownloadError) as error:
            raise SourceDownloadError(f"BEA schedule download failed: {error}") from error
        return self.parse_schedule(html)

    def parse_schedule(self, html: str) -> list[CalendarEvent]:
        """Extract GDP, PCE, and Core PCE schedule entries from BEA HTML."""
        text = " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())
        pattern = re.compile(
            r"(January|February|March|April|May|June|July|August|September|October|November|December)"
            r"\s+(\d{1,2})\s+(\d{1,2}:\d{2}\s+[AP]M).*?"
            r"(GDP[^.]*?|Personal Income and Outlays[^.]*?)(?=January|February|March|April|May|June|July|August|September|October|November|December|$)",
            re.IGNORECASE,
        )
        year = _schedule_year(text)
        events: list[CalendarEvent] = []
        for match in pattern.finditer(text):
            date = datetime.strptime(
                f"{match.group(1)} {match.group(2)} {year} {match.group(3)}",
                "%B %d %Y %I:%M %p",
            ).replace(tzinfo=EASTERN)
            release = match.group(4)
            if "GDP" in release.upper():
                events.append(_event("GDP", "gdp", date))
            if "PERSONAL INCOME AND OUTLAYS" in release.upper():
                events.extend((_event("PCE", "pce", date), _event("Core PCE", "core-pce", date)))
        if not events:
            raise SourceDownloadError("BEA schedule contained no supported releases")
        return events


def _schedule_year(text: str) -> int:
    found = re.search(r"Year\s+(20\d{2})", text, re.IGNORECASE)
    if not found:
        raise SourceDownloadError("BEA schedule year is missing")
    return int(found.group(1))


def _event(title: str, key: str, scheduled_at: datetime) -> CalendarEvent:
    return CalendarEvent(
        event_id=f"bea-{key}-{scheduled_at:%Y%m%d}",
        country="United States",
        title=title,
        scheduled_at=scheduled_at,
        markets=("Gold", "USD", "US Indices"),
        expected_volatility="High",
        source="BEA",
        source_url=BEA_SCHEDULE_URL,
        release_url="https://www.bea.gov/news/current-releases",
        impact=ImpactLevel.HIGH,
    )
