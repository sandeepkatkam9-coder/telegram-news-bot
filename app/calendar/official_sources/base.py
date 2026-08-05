"""Official-source HTTP adapter and schema validation."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from app.calendar.models.event import CalendarEvent


class Response(Protocol):
    """Minimal response contract, allowing deterministic tests."""

    def raise_for_status(self) -> None: ...

    def json(self) -> object: ...


class HttpClient(Protocol):
    """Minimal HTTP client contract."""

    def get(self, url: str, *, timeout: float) -> Response: ...


class CalendarSource(Protocol):
    """Common contract for calendar sources using their native media type."""

    name: str

    def fetch(self, client: object | None = None) -> list[CalendarEvent]: ...


class SourceDownloadError(RuntimeError):
    """An official publisher did not provide a usable schedule response."""


class UrlLibClient:
    """Small standard-library JSON client used when no client is injected."""

    def get(self, url: str, *, timeout: float) -> Response:
        try:
            with urlopen(url, timeout=timeout) as response:  # noqa: S310
                payload = response.read().decode("utf-8")
        except (HTTPError, URLError, UnicodeDecodeError) as error:
            raise SourceDownloadError(str(error)) from error
        return _JsonResponse(payload)


class _JsonResponse:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> object:
        try:
            return json.loads(self._payload)
        except json.JSONDecodeError as error:
            raise SourceDownloadError("publisher response is not JSON") from error


Parser = Callable[[object], list[CalendarEvent]]


class OfficialCalendarSource:
    """Downloads a structured release schedule from a first-party endpoint."""

    def __init__(self, name: str, url: str, parser: Parser) -> None:
        self.name = name
        self.url = url
        self._parser = parser

    def fetch(self, client: HttpClient | None = None) -> list[CalendarEvent]:
        """Download and parse events, raising on HTTP or publisher schema errors."""
        http = client or UrlLibClient()
        response = http.get(self.url, timeout=20.0)
        response.raise_for_status()
        return self._parser(response.json())
