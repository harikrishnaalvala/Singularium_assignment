"""Lightweight shared state for API interactions."""

from typing import Any, List, Optional

_LAST_ANALYZED_PAYLOAD: Optional[List[Any]] = None


def set_last_analyzed_payload(tasks: List[Any]) -> None:
    """Persist the last analyzed tasks payload in memory."""

    global _LAST_ANALYZED_PAYLOAD
    _LAST_ANALYZED_PAYLOAD = list(tasks) if tasks is not None else None


def get_last_analyzed_payload() -> Optional[List[Any]]:
    """Retrieve the cached tasks payload, if any."""

    return _LAST_ANALYZED_PAYLOAD
