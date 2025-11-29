"""
DependencyGraph
---------------

Responsible for detecting circular dependencies using DFS.

Input:
- tasks: Dict[id -> TaskEntity]

Output:
- has_cycle(): bool
- get_cycles(): list of lists of task IDs

"""

class DependencyGraph:

    def __init__(self, tasks_dict):
        self.tasks = tasks_dict
        self.visited = set()
        self.rec_stack = set()
        self.cycles = []

    def _reset_state(self):
        self.visited.clear()
        self.rec_stack.clear()
        self.cycles.clear()

    def _dfs(self, task_id, path):
        if task_id in self.rec_stack:
            cycle_start = path.index(task_id)
            self.cycles.append(path[cycle_start:])
            return

        if task_id in self.visited:
            return

        self.visited.add(task_id)
        self.rec_stack.add(task_id)

        task = self.tasks.get(task_id)
        if not task:
            self.rec_stack.remove(task_id)
            return

        for dep in task.dependencies:
            self._dfs(dep, path + [dep])

        self.rec_stack.remove(task_id)

    def _detect_cycles(self):
        self._reset_state()
        for task_id in self.tasks:
            self._dfs(task_id, [task_id])

    def has_cycle(self):
        self._detect_cycles()
        return bool(self.cycles)

    def get_cycles(self):
        if not self.cycles:
            self._detect_cycles()
        return self.cycles
