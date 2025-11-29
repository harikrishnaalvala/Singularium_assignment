"""Lightweight task validation utilities."""

from typing import Any, Dict, List, Tuple


class TaskValidator:
	"""Validate minimal invariants for task-like objects."""

	def validate(self, task: Any) -> Tuple[bool, List[Dict[str, str]]]:
		"""Return validation status and any issues discovered."""

		issues: List[Dict[str, str]] = []

		title = getattr(task, "title", "") or ""
		if not str(title).strip():
			issues.append({"field": "title", "message": "title is required"})

		importance = getattr(task, "importance", None)
		if importance is None:
			issues.append({"field": "importance", "message": "importance missing"})
		else:
			try:
				value = int(importance)
				if value < 0:
					issues.append({"field": "importance", "message": "importance must be positive"})
			except Exception:
				issues.append({"field": "importance", "message": "importance must be an integer"})

		due_date = getattr(task, "due_date", None)
		if due_date is None:
			issues.append({"field": "due_date", "message": "due date required"})

		estim = getattr(task, "estimated_hours", None)
		if estim is None:
			issues.append({"field": "estimated_hours", "message": "estimated hours required"})
		else:
			try:
				hours = float(estim)
				if hours <= 0:
					issues.append({"field": "estimated_hours", "message": "estimated hours must be positive"})
			except Exception:
				issues.append({"field": "estimated_hours", "message": "estimated hours must be numeric"})

		deps = getattr(task, "dependencies", None)
		if deps is not None and not isinstance(deps, list):
			issues.append({"field": "dependencies", "message": "dependencies must be a list"})

		return (len(issues) == 0), issues
