"""Async bridge between calendar rules and the existing Telegram sender."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime

from app.calendar.formatter.daily import DailyScheduleFormatter
from app.calendar.scheduler.scheduler import CalendarScheduler, IST

SendMessage = Callable[[str], Awaitable[None]]


class CalendarNotificationService:
    """Dispatches messages due during one scheduler tick."""

    def __init__(self, scheduler: CalendarScheduler, send_message: SendMessage) -> None:
        self._scheduler = scheduler
        self._send_message = send_message
        self._formatter = DailyScheduleFormatter()

    async def run_once(
        self,
        now: datetime,
        cot_positions: dict[str, str] | None = None,
    ) -> int:
        """Send daily, reminder, and Friday COT messages due at ``now``."""
        sent = 0
        local_now = now.astimezone(IST)
        if local_now.hour == 9 and local_now.minute == 0:
            message = self._scheduler.daily_message(now)
            if message:
                await self._send_message(message)
                sent += 1
        for event in self._scheduler.due_reminders(now):
            await self._send_message(self._formatter.reminder(event))
            sent += 1
        if cot_positions is not None and self._scheduler.weekly_cot_due(now):
            await self._send_message(self._formatter.cot_report(cot_positions))
            sent += 1
        return sent
