"""Catalog of allowed first-party calendar endpoints.

Sources are intentionally restricted to public, official publishers.  A source
adapter may be enabled only when it exposes a stable structured schedule feed;
no third-party calendar is scraped or used as a fallback.
"""

from __future__ import annotations

from app.calendar.official_sources.base import CalendarSource
from app.calendar.official_sources.bea import BeaSource
from app.calendar.official_sources.eia import EiaSource
from app.calendar.official_sources.fed import FedSource
from app.calendar.official_sources.bls import BlsSource


OFFICIAL_SCHEDULE_ENDPOINTS: dict[str, str] = {
    "Federal Reserve": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "BLS": "https://www.bls.gov/schedule/news_release/",
    "BEA": "https://apps.bea.gov/news/schedule/",
    "EIA": "https://www.eia.gov/reports/schedule/",
    "OPEC": "https://www.opec.org/opec_web/en/press_room/",
    "CFTC": "https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm",
    "ECB": "https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html",
    "BOE": "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes",
    "BoC": "https://www.bankofcanada.ca/core-functions/monetary-policy/key-interest-rate/",
    "RBA": "https://www.rba.gov.au/monetary-policy/rba-board-minutes/",
}


def default_sources() -> tuple[CalendarSource, ...]:
    """Return enabled official structured-feed adapters.

    BLS is the only active integration. All other URLs are an allow-list for
    future source-specific implementations and are not downloaded.
    """
    return (BlsSource(), BeaSource(), FedSource(), EiaSource())
