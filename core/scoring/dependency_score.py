"""
Dependency Score
----------------
Counts how many tasks depend on this task.
"""

def compute_dependency_score(task, task_map):
    count = 0
    for t in task_map.values():
        if task.id in t.dependencies:
            count += 1
    return count
