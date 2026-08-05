"""Run AutoTrade-HUB calendar updates and notification checks."""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime

from app.calendar.official_sources.catalog import default_sources
from app.calendar.scheduler.scheduler import CalendarScheduler
from app.calendar.service import CalendarNotificationService
from app.calendar.storage.repository import EventRepository
from app.calendar.updater.updater import CalendarUpdater
from app.telegram_sender import send_telegram

LOGGER = logging.getLogger("autotrade_hub.calendar")


async def run_once(refresh: bool) -> int:
    """Optionally refresh the calendar, then dispatch one notification tick."""
    repository = EventRepository()
    if refresh:
        result = CalendarUpdater(repository, default_sources()).update()
        if result.failures:
            LOGGER.error("calendar_update_failed failures=%s", result.failures)
        else:
            LOGGER.info(
                "calendar_updated source_count=%s event_count=%s",
                result.source_count,
                result.event_count,
            )
    service = CalendarNotificationService(CalendarScheduler(repository), send_telegram)
    sent = await service.run_once(datetime.now().astimezone())
    LOGGER.info("calendar_tick_complete messages_sent=%s", sent)
    return sent


async def run_forever(refresh_minutes: int) -> None:
    """Run a scheduler tick each minute and refresh the calendar periodically."""
    last_refresh: datetime | None = None
    while True:
        now = datetime.now().astimezone()
        refresh = last_refresh is None or (now - last_refresh).total_seconds() >= refresh_minutes * 60
        await run_once(refresh=refresh)
        if refresh:
            last_refresh = now
        await asyncio.sleep(60)


def main() -> None:
    """Configure structured logging and start the requested runner mode."""
    parser = argparse.ArgumentParser(description="AutoTrade-HUB calendar runner")
    parser.add_argument("--once", action="store_true", help="Run one scheduler tick")
    parser.add_argument("--no-refresh", action="store_true", help="Skip calendar refresh for --once")
    parser.add_argument("--refresh-minutes", type=int, default=360, help="Refresh interval in minutes")
    options = parser.parse_args()
    if options.refresh_minutes <= 0:
        parser.error("--refresh-minutes must be positive")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if options.once:
        asyncio.run(run_once(refresh=not options.no_refresh))
    else:
        asyncio.run(run_forever(options.refresh_minutes))


if __name__ == "__main__":
    main()
