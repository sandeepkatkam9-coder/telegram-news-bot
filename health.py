"""Print AutoTrade-HUB calendar health as JSON."""

from __future__ import annotations

import json

from app.calendar.health import inspect_calendar
from app.config import BOT_TOKEN, CHANNEL_ID


def main() -> None:
    """Run a read-only health inspection."""
    report = inspect_calendar().to_dict()
    report["telegram_status"] = "configured" if BOT_TOKEN and CHANNEL_ID else "not configured"
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
