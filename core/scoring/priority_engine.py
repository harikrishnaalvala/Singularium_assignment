"""
PriorityEngine
--------------

Combines all scoring components to compute a final score.

Methods:
- score_tasks(tasks: List[TaskEntity]) -> List[(task, score)]

This file orchestrates the multi-factor scoring process.
"""

from .urgency import compute_urgency
from .importance import compute_importance
from .effort import compute_effort
from .dependency_score import compute_dependency_score

class PriorityEngine:

    def __init__(self, config):
        self.config = config

    def score_task(self, task, task_map):
        urgency = compute_urgency(task, self.config)
        importance = compute_importance(task)
        effort = compute_effort(task)
        dependency = compute_dependency_score(task, task_map)

        score = (
            self.config.weight_urgency * urgency +
            self.config.weight_importance * importance +
            self.config.weight_effort * effort +
            self.config.weight_dependency * dependency
        )

        return score

    def score_tasks(self, tasks):
        task_map = {t.id: t for t in tasks}
        result = []

        for task in tasks:
            score = self.score_task(task, task_map)
            result.append((task, score))

        return sorted(result, key=lambda x: x[1], reverse=True)
