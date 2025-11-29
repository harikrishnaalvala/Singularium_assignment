"""
Data transfer objects for application layer.

These DTOs are thin adapters between incoming raw JSON and the domain TaskEntity.
They keep the application layer independent from HTTP or ORM specifics.

Inputs:
- raw task mapping from client

Outputs:
- TaskDTO instance with normalized fields

Note:
This module intentionally keeps conversions simple and deterministic to aid testing.
"""

from dataclasses import dataclass
from typing import List, Optional
import datetime


@dataclass
class TaskDTO:
    """
    TaskDTO represents a normalized task for the application boundary.

    Attributes:
        id: optional identifier, str or None
        title: normalized title string
        due_date: datetime.date object
        estimated_hours: float normalized to positive values
        importance: integer in allowed range
        dependencies: list of dependency ids as strings
        raw: original raw input dict for traceability
    """
    id: Optional[str]
    title: str
    due_date: datetime.date
    estimated_hours: float
    importance: int
    dependencies: List[str]
    raw: dict


def to_task_dto(raw: dict, date_parser) -> TaskDTO:
    """
    Convert raw dict to TaskDTO.

    Inputs:
        raw: raw task dictionary from client
        date_parser: callable that accepts a raw date value and returns datetime.date

    Output:
        TaskDTO with normalized fields

    Behavior:
        - attempts to parse due date via date_parser; on failure falls back to far future date
        - coerces estimated hours to float and ensures positivity
        - coerces importance to int and relies on validators elsewhere to clamp
        - converts dependency entries to strings
    """
    tid = raw.get("id") or raw.get("task_id") or None
    title = (raw.get("title") or "Untitled Task").strip()
    due_date = date_parser(raw.get("due_date"))
    try:
        est = float(raw.get("estimated_hours"))
        if est <= 0:
            est = float(raw.get("estimated_hours") or 1.0)
    except Exception:
        est = float(1.0)
    try:
        importance = int(raw.get("importance") or 1)
    except Exception:
        importance = 1
    deps = raw.get("dependencies") or []
    if not isinstance(deps, list):
        deps = []
    deps = [str(d) for d in deps if d is not None]
    return TaskDTO(
        id=str(tid) if tid is not None else None,
        title=title,
        due_date=due_date,
        estimated_hours=est,
        importance=importance,
        dependencies=deps,
        raw=raw
    )
