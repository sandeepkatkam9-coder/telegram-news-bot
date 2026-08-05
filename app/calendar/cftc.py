"""Official CFTC Commitment of Traders downloader and Telegram formatter."""

from __future__ import annotations

from app.calendar.cot import CotPosition, parse_legacy_csv
from app.calendar.official_sources.bls import UrlLibTextClient
from app.calendar.official_sources.base import SourceDownloadError

CFTC_LEGACY_URL = "https://www.cftc.gov/dea/newcot/deacot.txt"


class CftcCotSource:
    """Downloads the CFTC's current official Legacy Futures Only report."""

    name = "CFTC"

    def fetch_positions(self, client: object | None = None) -> list[CotPosition]:
        """Return supported market positions from the latest official COT file."""
        try:
            payload = (client or UrlLibTextClient()).get_text(CFTC_LEGACY_URL, timeout=20.0)  # type: ignore[attr-defined]
        except Exception as error:
            raise SourceDownloadError(f"CFTC COT download failed: {error}") from error
        positions = parse_legacy_csv(payload)
        if not positions:
            raise SourceDownloadError("CFTC COT file contained no supported markets")
        return positions


def telegram_report(positions: list[CotPosition]) -> str:
    """Render official CFTC figures only; no directional market interpretation."""
    lines = ["📊 WEEKLY COT REPORT", ""]
    for position in positions:
        lines.extend(
            (
                f"{position.market}",
                f"Open Interest: {position.open_interest:,}",
                f"Commercial: L {position.commercial_long:,} / S {position.commercial_short:,}",
                f"Large Speculators: L {position.large_speculators_long:,} / S {position.large_speculators_short:,}",
                f"Retail / Non-reportable: L {position.retail_long:,} / S {position.retail_short:,}",
                "",
            )
        )
    lines.append("AutoTrade-HUB")
    return "\n".join(lines)
