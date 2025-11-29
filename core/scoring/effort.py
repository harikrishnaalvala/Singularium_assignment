"""
Effort Score
------------

Low effort = higher score
"""

def compute_effort(task):
    return 1 / max(task.estimated_hours, 1)
