"""
TaskEntity
----------

Represents a single task in the domain layer.

Inputs:
- title: str
- due_date: datetime.date
- estimated_hours: float
- importance: int
- dependencies: list of task IDs (strings or ints)

Output:
- Simple object containing task data

Note:
This entity contains no framework-specific logic to keep the domain pure.
"""

from dataclasses import dataclass
from typing import List, Optional
import datetime


@dataclass
class TaskEntity:
    id: Optional[str]
    title: str
    due_date: datetime.date
    estimated_hours: float
    importance: int
    dependencies: List[str]
