"""Official United States Bureau of Labor Statistics calendar adapter."""

from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from html import unescape
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from app.calendar.models.event import CalendarEvent, ImpactLevel
from app.calendar.official_sources.base import SourceDownloadError
from app.calendar.scheduler.release import ReleaseValues

LOGGER = logging.getLogger(__name__)
BLS_CALENDAR_URL = "https://www.bls.gov/schedule/news_release/bls.ics"
BLS_BASE_URL = "https://www.bls.gov"
EASTERN = ZoneInfo("America/New_York")
RETRIES = 3
TIMEOUT_SECONDS = 20.0


class TextClient(Protocol):
    """Minimal injectable text client for BLS requests."""

    def get_text(self, url: str, *, timeout: float) -> str: ...


class BlsSource:
    """Downloads BLS's official ICS release calendar and release pages."""

    name = "BLS"

    def __init__(self, sleep: Callable[[float], None] = time.sleep) -> None:
        self._sleep = sleep

    def fetch(self, client: TextClient | None = None) -> list[CalendarEvent]:
        """Download and normalize BLS's supported future economic releases."""
        calendar = self._download(BLS_CALENDAR_URL, client)
        return self.parse_schedule(calendar)

    def fetch_release(self, event: CalendarEvent, client: TextClient | None = None) -> ReleaseValues:
        """Download official released values for one supported BLS event."""
        if not event.release_url:
            raise SourceDownloadError(f"BLS release URL missing for {event.event_id}")
        document = self._download(event.release_url, client)
        values = self.parse_release(document, event.title)
        if values.actual is None:
            raise SourceDownloadError(f"BLS actual value missing for {event.title}")
        return values

    def fetch_released_event(
        self,
        event: CalendarEvent,
        client: TextClient | None = None,
    ) -> CalendarEvent:
        """Return the supplied event enriched with official actual/previous data."""
        values = self.fetch_release(event, client)
        return replace(event, actual=values.actual, previous=values.previous)

    def parse_schedule(self, calendar: str) -> list[CalendarEvent]:
        """Parse the official iCalendar document into the six supported events."""
        events: list[CalendarEvent] = []
        for item in _icalendar_events(calendar):
            summary = item.get("SUMMARY", "")
            scheduled_at = _parse_icalendar_datetime(item.get("DTSTART", ""))
            if scheduled_at is None:
                LOGGER.warning("Skipping BLS calendar event with no valid DTSTART: %s", summary)
                continue
            events.extend(_normalize_schedule_event(summary, scheduled_at))
        if not events:
            raise SourceDownloadError("BLS calendar contained no supported release events")
        return events

    def parse_release(self, html: str, title: str) -> ReleaseValues:
        """Extract supported released values from the official BLS release HTML."""
        text = _page_text(html)
        parsers: dict[str, Callable[[str], ReleaseValues]] = {
            "Consumer Price Index (CPI)": _parse_cpi,
            "Core CPI": _parse_core_cpi,
            "Producer Price Index (PPI)": _parse_ppi,
            "Non-Farm Payrolls (NFP)": _parse_nfp,
            "Unemployment Rate": _parse_unemployment,
            "Average Hourly Earnings": _parse_hourly_earnings,
        }
        try:
            return parsers[title](text)
        except KeyError as error:
            raise SourceDownloadError(f"Unsupported BLS release event: {title}") from error

    def _download(self, url: str, client: TextClient | None) -> str:
        http = client or UrlLibTextClient()
        error: Exception | None = None
        for attempt in range(RETRIES):
            try:
                return http.get_text(url, timeout=TIMEOUT_SECONDS)
            except (HTTPError, URLError, TimeoutError, OSError, SourceDownloadError) as exc:
                error = exc
                if attempt < RETRIES - 1:
                    delay = 2**attempt
                    LOGGER.warning("BLS download failed (%s); retrying in %ss", exc, delay)
                    self._sleep(delay)
        raise SourceDownloadError(f"BLS download failed after {RETRIES} attempts: {url}") from error


class UrlLibTextClient:
    """Standard-library HTTP implementation used in production."""

    def get_text(self, url: str, *, timeout: float) -> str:
        try:
            request = Request(
                url,
                headers={
                    "Accept": "text/calendar, text/html;q=0.9, */*;q=0.8",
                    "User-Agent": (
                        "AutoTrade-HUB/1.0 "
                        "(+https://github.com/sandeepkatkam9-coder/telegram-news-bot)"
                    ),
                },
            )
            with urlopen(request, timeout=timeout) as response:  # noqa: S310
                return response.read().decode("utf-8")
        except (HTTPError, URLError, UnicodeDecodeError) as error:
            raise SourceDownloadError(str(error)) from error


def _icalendar_events(document: str) -> list[dict[str, str]]:
    unfolded = re.sub(r"\r?\n[ \t]", "", document)
    results: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in unfolded.splitlines():
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT" and current is not None:
            results.append(current)
            current = None
        elif current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.split(";", 1)[0]] = unescape(value.replace("\\,", ","))
    return results


def _parse_icalendar_datetime(value: str) -> datetime | None:
    value = value.strip()
    try:
        if value.endswith("Z"):
            return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC"))
        return datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=EASTERN)
    except ValueError:
        return None


def _normalize_schedule_event(summary: str, scheduled_at: datetime) -> list[CalendarEvent]:
    summary = " ".join(summary.split())
    mappings = {
        "Consumer Price Index": (
            ("Consumer Price Index (CPI)", "cpi"),
            ("Core CPI", "core-cpi"),
        ),
        "Producer Price Index": (("Producer Price Index (PPI)", "ppi"),),
        "Employment Situation": (
            ("Non-Farm Payrolls (NFP)", "nfp"),
            ("Unemployment Rate", "unemployment-rate"),
            ("Average Hourly Earnings", "average-hourly-earnings"),
        ),
    }
    for marker, definitions in mappings.items():
        if marker in summary:
            return [_event(name, key, scheduled_at) for name, key in definitions]
    return []


def _event(title: str, key: str, scheduled_at: datetime) -> CalendarEvent:
    release = {
        "cpi": "cpi",
        "core-cpi": "cpi",
        "ppi": "ppi",
        "nfp": "empsit",
        "unemployment-rate": "empsit",
        "average-hourly-earnings": "empsit",
    }[key]
    return CalendarEvent(
        event_id=f"bls-{key}-{scheduled_at:%Y%m%d}",
        country="United States",
        title=title,
        scheduled_at=scheduled_at,
        markets=("Gold", "USD", "US Indices"),
        expected_volatility="High",
        source="BLS",
        source_url=BLS_CALENDAR_URL,
        release_url=f"{BLS_BASE_URL}/news.release/{release}.nr0.htm",
        impact=ImpactLevel.HIGH,
    )


def _page_text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def _match(text: str, pattern: str) -> ReleaseValues:
    found = re.search(pattern, text, flags=re.IGNORECASE)
    if not found:
        return ReleaseValues(actual=None)
    actual = _signed(found.group(1), found.group(2))
    previous = _signed(found.group(3), found.group(4)) if found.lastindex and found.lastindex >= 4 else None
    return ReleaseValues(actual=actual, previous=previous)


def _signed(direction: str, number: str) -> str:
    if direction.lower() in {"decreased", "fell", "declined"}:
        return f"-{number}%"
    if direction.lower() == "unchanged":
        return "0.0%"
    return f"{number}%"


def _parse_cpi(text: str) -> ReleaseValues:
    return _match(text, r"CPI-U\) (increased|decreased) ([\d.]+) percent.*?after (rising|falling) ([\d.]+) percent")


def _parse_core_cpi(text: str) -> ReleaseValues:
    return _match(
        text,
        r"all items less food and energy (rose|fell) ([\d.]+) percent.*?after (rising|falling) ([\d.]+) percent",
    )


def _parse_ppi(text: str) -> ReleaseValues:
    return _match(text, r"Final demand (increased|decreased) ([\d.]+) percent.*?after (increasing|decreasing) ([\d.]+) percent")


def _parse_nfp(text: str) -> ReleaseValues:
    found = re.search(r"Total nonfarm payroll employment (increased|decreased) by ([\d,]+)", text, re.I)
    return ReleaseValues(actual=_signed_count(found) if found else None)


def _parse_unemployment(text: str) -> ReleaseValues:
    found = re.search(r"unemployment rate (?:was )?(?:unchanged at )?([\d.]+) percent", text, re.I)
    return ReleaseValues(actual=f"{found.group(1)}%" if found else None)


def _parse_hourly_earnings(text: str) -> ReleaseValues:
    found = re.search(r"average hourly earnings.*?(rose|fell) (\d+) cents, or ([\d.]+) percent", text, re.I)
    return ReleaseValues(actual=_signed(found.group(1), found.group(3)) if found else None)


def _signed_count(found: re.Match[str]) -> str:
    sign = "-" if found.group(1).lower() == "decreased" else "+"
    return f"{sign}{found.group(2)}"
