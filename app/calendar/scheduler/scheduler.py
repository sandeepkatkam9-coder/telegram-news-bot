"""Daily, reminder, and weekly schedule rules."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.calendar.formatter.daily import DailyScheduleFormatter
from app.calendar.models.event import CalendarEvent
from app.calendar.storage.repository import EventRepository

IST = ZoneInfo("Asia/Kolkata")


class CalendarScheduler:
    """Evaluates notification rules against persisted calendar events."""

    def __init__(self, repository: EventRepository, formatter: DailyScheduleFormatter | None = None) -> None:
        self._repository = repository
        self._formatter = formatter or DailyScheduleFormatter()

    def daily_message(self, now: datetime) -> str | None:
        """Return the 09:00 IST schedule, or None when every event is past."""
        local_now = now.astimezone(IST)
        day_events = [
            event for event in self._repository.load()
            if event.is_major and event.scheduled_at.astimezone(IST).date() == local_now.date()
        ]
        if not day_events:
            return self._formatter.daily_schedule([])
        after_nine = [event for event in day_events if event.scheduled_at.astimezone(IST).time() > local_now.replace(hour=9, minute=0, second=0, microsecond=0).time()]
        if not after_nine:
            return None
        return self._formatter.daily_schedule(after_nine)

    def due_reminders(self, now: datetime) -> list[CalendarEvent]:
        """Return high-impact events whose 30-minute reminder is currently due."""
        local_now = now.astimezone(IST)
        lower = local_now + timedelta(minutes=29)
        upper = local_now + timedelta(minutes=31)
        return [
            event for event in self._repository.load()
            if event.is_major and lower <= event.scheduled_at.astimezone(IST) <= upper
        ]

    def weekly_cot_due(self, now: datetime) -> bool:
        """COT reports are generated on Fridays after the CFTC publication time."""
        local_now = now.astimezone(IST)
        return local_now.weekday() == 4 and local_now.hour >= 20
