"""
Urgency Score
-------------

Computes urgency score based on due date.

Input:
- task: TaskEntity
- config: ScoringConfig

Output:
- float urgency score
"""

import math
from datetime import date

def compute_urgency(task, config):
    today = date.today()
    delta = (task.due_date - today).days

    # overdue case
    if delta < 0:
        overdue_days = abs(delta)
        return config.overdue_base + overdue_days * config.overdue_growth

    if config.urgency_mode == "linear":
        return 1 / max(delta, 1)

    if config.urgency_mode == "exponential":
        return math.exp(-delta)

    if config.urgency_mode == "threshold":
        if delta <= config.urgency_threshold:
            return config.high_urgency_value
        return config.low_urgency_value

    return 0
