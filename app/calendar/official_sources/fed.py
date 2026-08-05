"""Federal Reserve FOMC calendar adapter."""
from __future__ import annotations
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.calendar.models.event import CalendarEvent, ImpactLevel
from app.calendar.official_sources.base import SourceDownloadError
from app.calendar.official_sources.bls import UrlLibTextClient

FED_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
EASTERN = ZoneInfo("America/New_York")

class FedSource:
    name = "Federal Reserve"
    def fetch(self, client: object | None = None) -> list[CalendarEvent]:
        try:
            html = (client or UrlLibTextClient()).get_text(FED_URL, timeout=20.0)  # type: ignore[attr-defined]
        except Exception as error:
            raise SourceDownloadError(f"Federal Reserve schedule download failed: {error}") from error
        return self.parse_schedule(html)
    def parse_schedule(self, html: str) -> list[CalendarEvent]:
        text = " ".join(re.sub(r"<[^>]+>", " ", html).split())
        year_match = re.search(r"(20\d{2}) FOMC Meetings", text)
        if not year_match: raise SourceDownloadError("FOMC schedule year missing")
        year = int(year_match.group(1)); events=[]
        months = "January|February|March|April|May|June|July|August|September|October|November|December"
        for month, start, finish in re.findall(rf"({months})\s+(\d{{1,2}})(?:-(\d{{1,2}}))?", text):
            end = int(finish or start)
            date = datetime.strptime(f"{month} {end} {year} 02:00 PM", "%B %d %Y %I:%M %p").replace(tzinfo=EASTERN)
            events.extend((_event("FOMC Interest Rate Decision", "decision", date), _event("Fed Press Conference", "press-conference", date + timedelta(minutes=30))))
        if not events: raise SourceDownloadError("FOMC schedule contained no meetings")
        return events

def _event(title: str, key: str, when: datetime) -> CalendarEvent:
    return CalendarEvent(f"fed-{key}-{when:%Y%m%d}", "United States", title, when, ("Gold", "USD", "US Indices"), "High", "Federal Reserve", FED_URL, ImpactLevel.HIGH, release_url=FED_URL)
