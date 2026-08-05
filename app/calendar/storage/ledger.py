"""Persistent idempotency ledger for calendar notifications."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


class DeliveryLedger:
    """Records successfully sent notification keys across process restarts."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(__file__).with_name("delivery_ledger.json")

    def contains(self, key: str) -> bool:
        """Return whether a message with ``key`` was already sent."""
        return key in self._load()

    def record(self, key: str) -> None:
        """Persist a successful delivery atomically."""
        entries = self._load()
        entries[key] = datetime.now(UTC).isoformat()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)

    def _load(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        content = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            raise ValueError("invalid calendar delivery ledger")
        return {str(key): str(value) for key, value in content.items()}
