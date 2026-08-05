"""Async bridge between calendar rules and the existing Telegram sender."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime

from app.calendar.formatter.daily import DailyScheduleFormatter
from app.calendar.scheduler.scheduler import CalendarScheduler, IST
from app.calendar.storage.ledger import DeliveryLedger

SendMessage = Callable[[str], Awaitable[None]]


class CalendarNotificationService:
    """Dispatches messages due during one scheduler tick."""

    def __init__(
        self,
        scheduler: CalendarScheduler,
        send_message: SendMessage,
        ledger: DeliveryLedger | None = None,
    ) -> None:
        self._scheduler = scheduler
        self._send_message = send_message
        self._formatter = DailyScheduleFormatter()
        self._ledger = ledger or DeliveryLedger()

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
                sent += await self._deliver(f"daily:{local_now.date().isoformat()}", message)
        for event in self._scheduler.due_reminders(now):
            sent += await self._deliver(
                f"reminder:{event.event_id}",
                self._formatter.reminder(event),
            )
        if cot_positions is not None and self._scheduler.weekly_cot_due(now):
            week = local_now.strftime("%G-W%V")
            sent += await self._deliver(f"cot:{week}", self._formatter.cot_report(cot_positions))
        return sent

    async def _deliver(self, key: str, message: str) -> int:
        if self._ledger.contains(key):
            return 0
        await self._send_message(message)
        self._ledger.record(key)
        return 1
