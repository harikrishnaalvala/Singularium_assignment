"""
ScoringConfig
-------------

Configuration object for weights + modes.
"""

from dataclasses import dataclass

@dataclass
class ScoringConfig:
    weight_urgency: float = 1.0
    weight_importance: float = 1.0
    weight_effort: float = 0.5
    weight_dependency: float = 1.0

    urgency_mode: str = "linear"

    overdue_base: float = 5
    overdue_growth: float = 1

    urgency_threshold: int = 2
    high_urgency_value: float = 2
    low_urgency_value: float = 0.5
