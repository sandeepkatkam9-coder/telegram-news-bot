"""Human-readable, Telegram-safe calendar messages."""

from __future__ import annotations

from app.calendar.models.event import CalendarEvent


class DailyScheduleFormatter:
    """Formats daily schedules, reminders, releases, and COT reports."""

    divider = "━━━━━━━━━━━━━━━━━━━━"

    def daily_schedule(self, events: list[CalendarEvent]) -> str:
        """Format a daily high-impact schedule."""
        if not events:
            return (
                "📅 DAILY MARKET SCHEDULE\n\n"
                "No Major High Impact Economic Events Scheduled Today.\n\n"
                f"{self.divider}\n\n"
                "Wishing you a successful trading day!\n\nAutoTrade-HUB"
            )
        lines = ["📅 DAILY MARKET SCHEDULE", ""]
        for event in events:
            lines.extend(
                (
                    f"🇺🇳 {event.country}",
                    f"📌 {event.title}",
                    f"🕒 {event.scheduled_at:%I:%M %p IST}",
                    f"📈 Markets: {', '.join(event.markets)}",
                    f"⚡ Expected Volatility: {event.expected_volatility}",
                    self.divider,
                )
            )
        lines.extend(("", "Wishing you a successful trading day!", "", "AutoTrade-HUB"))
        return "\n".join(lines)

    def reminder(self, event: CalendarEvent) -> str:
        """Format the mandatory 30-minute warning."""
        return "\n".join(
            (
                "⏰ HIGH IMPACT NEWS IN 30 MINUTES",
                "",
                f"Country: {event.country}",
                f"Event: {event.title}",
                f"Time: {event.scheduled_at:%I:%M %p IST}",
                f"Markets: {', '.join(event.markets)}",
                f"Expected Volatility: {event.expected_volatility}",
            )
        )

    def release(self, event: CalendarEvent, result: str) -> str:
        """Format a release notification using official published values."""
        return "\n".join(
            (
                "🚨 HIGH IMPACT NEWS RELEASED",
                "",
                f"Country: {event.country}",
                f"Event: {event.title}",
                f"Actual: {event.actual or 'Pending'}",
                f"Previous: {event.previous or 'N/A'}",
                f"Result: {result}",
                f"Markets: {', '.join(event.markets)}",
            )
        )

    def cot_report(self, positions: dict[str, str]) -> str:
        """Format the weekly CFTC Commitment of Traders report."""
        required = ("Gold", "Silver", "WTI", "USD Index", "Bitcoin")
        lines = ["📊 WEEKLY COT REPORT", ""]
        lines.extend(f"{market}: {positions.get(market, 'Not published')}" for market in required)
        lines.extend(("", self.divider, "", "AutoTrade-HUB"))
        return "\n".join(lines)
