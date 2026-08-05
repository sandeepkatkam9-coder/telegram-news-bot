"""Unit tests for the AutoTrade-HUB economic calendar."""

from __future__ import annotations

import json
import asyncio
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from app.calendar.formatter.daily import DailyScheduleFormatter
from app.calendar.models.event import CalendarEvent, ImpactLevel
from app.calendar.official_sources.base import OfficialCalendarSource
from app.calendar.official_sources.bls import BlsSource
from app.calendar.official_sources.catalog import OFFICIAL_SCHEDULE_ENDPOINTS, default_sources
from app.calendar.scheduler.release import ReleaseEngine, ReleaseValues
from app.calendar.scheduler.scheduler import CalendarScheduler
from app.calendar.service import CalendarNotificationService
from app.calendar.storage.ledger import DeliveryLedger
from app.calendar.storage.repository import EventRepository
from app.calendar.updater.updater import CalendarUpdater


def temporary_directory() -> tempfile.TemporaryDirectory[str]:
    """Create test files inside the writable repository sandbox."""
    return tempfile.TemporaryDirectory(dir=Path.cwd())


def event(hour: int = 10, impact: ImpactLevel = ImpactLevel.HIGH) -> CalendarEvent:
    return CalendarEvent(
        event_id="bls-cpi-2026-01",
        country="United States",
        title="Consumer Price Index",
        scheduled_at=datetime(2026, 1, 2, hour, 0, tzinfo=UTC),
        markets=("Gold", "USD"),
        expected_volatility="High",
        source="BLS",
        source_url="https://www.bls.gov/",
        forecast="2.5",
        impact=impact,
    )


class RepositoryTests(unittest.TestCase):
    def test_model_round_trip_and_repository_document(self) -> None:
        with temporary_directory() as directory:
            repository = EventRepository(Path(directory) / "events.json")
            repository.save([event()], source_count=1)
            self.assertEqual(repository.load(), [event()])
            document = json.loads(repository.path.read_text(encoding="utf-8"))
            self.assertEqual(document["event_count"], 1)
            self.assertEqual(document["version"], 1)

    def test_model_rejects_naive_date(self) -> None:
        with self.assertRaises(ValueError):
            CalendarEvent(
                event_id="id",
                country="US",
                title="CPI",
                scheduled_at=datetime(2026, 1, 1),
                markets=("USD",),
                expected_volatility="High",
                source="BLS",
                source_url="https://www.bls.gov/",
            )


class FormatterAndSchedulerTests(unittest.TestCase):
    def test_daily_empty_message_matches_required_copy(self) -> None:
        message = DailyScheduleFormatter().daily_schedule([])
        self.assertIn("No Major High Impact Economic Events Scheduled Today.", message)
        self.assertIn("AutoTrade-HUB", message)

    def test_daily_and_reminder_rules(self) -> None:
        with temporary_directory() as directory:
            repository = EventRepository(Path(directory) / "events.json")
            repository.save([event(hour=5)], source_count=1)  # 10:30 AM IST
            scheduler = CalendarScheduler(repository)
            now = datetime(2026, 1, 2, 4, 0, tzinfo=UTC)  # 09:30 AM IST
            self.assertIn("Consumer Price Index", scheduler.daily_message(now) or "")
            due = scheduler.due_reminders(datetime(2026, 1, 2, 4, 30, tzinfo=UTC))
            self.assertEqual(due, [event(hour=5)])
            self.assertTrue(scheduler.weekly_cot_due(datetime(2026, 1, 2, 15, 0, tzinfo=UTC)))

    def test_all_events_before_nine_suppresses_schedule(self) -> None:
        with temporary_directory() as directory:
            repository = EventRepository(Path(directory) / "events.json")
            repository.save([event(hour=1)], source_count=1)  # 06:30 AM IST
            self.assertIsNone(CalendarScheduler(repository).daily_message(datetime(2026, 1, 2, 4, tzinfo=UTC)))

    def test_release_engine_and_cot_formatter(self) -> None:
        released, result = ReleaseEngine().apply(event(), "3.0", "2.8")
        self.assertEqual(released.actual, "3.0")
        self.assertEqual(result, "Actual above forecast.")
        report = DailyScheduleFormatter().cot_report({"Gold": "Net long"})
        self.assertIn("Bitcoin: Not published", report)

    def test_release_engine_fetches_official_values(self) -> None:
        class Fetcher:
            def fetch_release(self, calendar_event: CalendarEvent) -> ReleaseValues:
                self.event_id = calendar_event.event_id
                return ReleaseValues(actual="2.1", previous="2.0")

        fetcher = Fetcher()
        released, result = ReleaseEngine().fetch_and_apply(event(), fetcher)
        self.assertEqual(fetcher.event_id, "bls-cpi-2026-01")
        self.assertEqual(released.previous, "2.0")
        self.assertEqual(result, "Actual below forecast.")

    def test_notification_service_dispatches_daily_message_at_nine_ist(self) -> None:
        with temporary_directory() as directory:
            repository = EventRepository(Path(directory) / "events.json")
            repository.save([], source_count=0)
            messages: list[str] = []

            async def send(message: str) -> None:
                messages.append(message)

            service = CalendarNotificationService(
                CalendarScheduler(repository),
                send,
                DeliveryLedger(Path(directory) / "ledger.json"),
            )
            count = asyncio.run(service.run_once(datetime(2026, 1, 2, 3, 30, tzinfo=UTC)))
            self.assertEqual(count, 1)
            self.assertIn("DAILY MARKET SCHEDULE", messages[0])

    def test_delivery_ledger_prevents_duplicate_daily_messages(self) -> None:
        with temporary_directory() as directory:
            repository = EventRepository(Path(directory) / "events.json")
            repository.save([], source_count=0)
            ledger = DeliveryLedger(Path(directory) / "ledger.json")
            messages: list[str] = []

            async def send(message: str) -> None:
                messages.append(message)

            service = CalendarNotificationService(CalendarScheduler(repository), send, ledger)
            now = datetime(2026, 1, 2, 3, 30, tzinfo=UTC)
            self.assertEqual(asyncio.run(service.run_once(now)), 1)
            self.assertEqual(asyncio.run(service.run_once(now)), 0)
            self.assertEqual(len(messages), 1)


class _Response:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> object:
        return {"events": []}


class _Client:
    def get(self, url: str, *, timeout: float) -> _Response:
        return _Response()


class OfficialSourceAndUpdaterTests(unittest.TestCase):
    def test_official_catalog_is_restricted_to_requested_publishers(self) -> None:
        self.assertEqual(len(OFFICIAL_SCHEDULE_ENDPOINTS), 10)
        self.assertEqual(default_sources()[0].name, "BLS")

    def test_source_download_and_updater_persist_events(self) -> None:
        source = OfficialCalendarSource("BLS", "https://www.bls.gov/feed", lambda payload: [event()])
        with temporary_directory() as directory:
            repository = EventRepository(Path(directory) / "events.json")
            result = CalendarUpdater(repository, (source,)).update(_Client())
            self.assertEqual(result.event_count, 1)
            self.assertEqual(result.source_count, 1)
            self.assertEqual(repository.load(), [event()])


BLS_ICALENDAR = """BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTART;TZID=America/New_York:20260812T083000
SUMMARY:Consumer Price Index for July 2026
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=America/New_York:20260813T083000
SUMMARY:Producer Price Index for July 2026
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=America/New_York:20260807T083000
SUMMARY:Employment Situation for July 2026
END:VEVENT
END:VCALENDAR
"""


class _BlsClient:
    def __init__(self, response: str = BLS_ICALENDAR, failures: int = 0) -> None:
        self.response = response
        self.failures = failures
        self.calls = 0

    def get_text(self, url: str, *, timeout: float) -> str:
        self.calls += 1
        if self.calls <= self.failures:
            raise TimeoutError("timed out")
        return self.response


class BlsSourceTests(unittest.TestCase):
    def test_successful_schedule_download_normalizes_six_events(self) -> None:
        events = BlsSource(sleep=lambda _: None).fetch(_BlsClient())
        self.assertEqual(len(events), 6)
        self.assertEqual(events[0].country, "United States")
        self.assertTrue(events[0].release_url.endswith(".nr0.htm"))

    def test_schedule_parser_ignores_unrelated_releases(self) -> None:
        events = BlsSource(sleep=lambda _: None).parse_schedule(
            BLS_ICALENDAR.replace("Consumer Price Index", "Productivity and Costs")
        )
        self.assertEqual(len(events), 4)

    def test_release_parsers_extract_supported_values(self) -> None:
        source = BlsSource(sleep=lambda _: None)
        cpi = source.parse_release(
            "CPI-U) increased 0.3 percent in May after rising 0.2 percent in April",
            "Consumer Price Index (CPI)",
        )
        nfp = source.parse_release(
            "Total nonfarm payroll employment increased by 150,000 in May",
            "Non-Farm Payrolls (NFP)",
        )
        self.assertEqual((cpi.actual, cpi.previous), ("0.3%", "0.2%"))
        self.assertEqual(nfp.actual, "+150,000")

    def test_released_event_is_normalized_with_official_values(self) -> None:
        event_to_release = next(
            item
            for item in BlsSource(sleep=lambda _: None).parse_schedule(BLS_ICALENDAR)
            if item.title == "Consumer Price Index (CPI)"
        )
        released = BlsSource(sleep=lambda _: None).fetch_released_event(
            event_to_release,
            _BlsClient("CPI-U) increased 0.3 percent in May after rising 0.2 percent in April"),
        )
        self.assertEqual((released.actual, released.previous), ("0.3%", "0.2%"))

    def test_release_parser_reports_missing_value(self) -> None:
        values = BlsSource(sleep=lambda _: None).parse_release("unexpected BLS page", "Producer Price Index (PPI)")
        self.assertIsNone(values.actual)

    def test_network_failure_retries_and_raises_meaningful_error(self) -> None:
        client = _BlsClient(failures=3)
        with self.assertRaisesRegex(Exception, "after 3 attempts"):
            BlsSource(sleep=lambda _: None).fetch(client)
        self.assertEqual(client.calls, 3)

    def test_bls_update_persists_calendar(self) -> None:
        with temporary_directory() as directory:
            repository = EventRepository(Path(directory) / "events.json")
            result = CalendarUpdater(repository, (BlsSource(sleep=lambda _: None),)).update(_BlsClient())
            self.assertEqual(result.event_count, 6)
            self.assertEqual(repository.load()[0].source, "BLS")

    def test_bls_update_preserves_previous_calendar_on_failure(self) -> None:
        with temporary_directory() as directory:
            repository = EventRepository(Path(directory) / "events.json")
            repository.save([event()], source_count=1)
            result = CalendarUpdater(repository, (BlsSource(sleep=lambda _: None),)).update(_BlsClient(failures=3))
            self.assertTrue(result.failures)
            self.assertEqual(repository.load(), [event()])


if __name__ == "__main__":
    unittest.main()
