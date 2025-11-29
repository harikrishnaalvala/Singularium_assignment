"""
Application service that produces top suggestions for today.

Responsibilities:
- reuse analyze service to compute scores
- provide human-friendly reasons for each suggestion
- limit suggestions to top n items based on score and business heuristics
- prefer unblocked tasks and those with actionable attributes

Inputs:
- tasks_payload: list of raw task dicts
- config_overrides: optional mapping
- top_n: number of suggestions to return

Outputs:
- list of suggestion mappings with fields:
    - id, title, score, reason, due_date, importance, estimated_hours, status
"""

from typing import List, Dict
from datetime import date

from application.services.analyze_tasks_service import analyze_tasks_service


def _make_reason(task_rec: Dict) -> str:
    """
    Compose human friendly reason string explaining why a task is suggested.

    Inputs:
        task_rec: enriched task mapping produced by analyze service

    Outputs:
        short explanatory string
    """
    if task_rec.get("blocked"):
        return "Task blocked by circular dependency"
    reasons = []
    if "passed" in task_rec.get("explanation", "") or "overdue" in task_rec.get("explanation", ""):
        reasons.append("past due")
    if task_rec.get("importance", 0) >= 8:
        reasons.append("high impact")
    if task_rec.get("estimated_hours", 0) <= 2:
        reasons.append("quick win")
    if not reasons:
        reasons.append("balanced priority")
    return ", ".join(reasons)


def suggest_tasks_service(tasks_payload: List[Dict], config_overrides: Dict = None, top_n: int = 3) -> List[Dict]:
    """
    Suggest top tasks to work on today.

    Inputs:
        tasks_payload: list of raw task dicts
        config_overrides: optional mapping to customize scoring
        top_n: number of suggestions to return

    Outputs:
        list of suggestion mapping objects
    """
    analysis = analyze_tasks_service(tasks_payload, config_overrides)
    candidates = analysis["priority_list"]

    # simple heuristic: pick top scoring tasks that are not blocked
    suggestions = []
    for rec in candidates:
        if len(suggestions) >= top_n:
            break
        suggestions.append({
            "id": rec["id"],
            "title": rec["title"],
            "score": rec["score"],
            "reason": _make_reason(rec),
            "due_date": rec["due_date"],
            "importance": rec["importance"],
            "estimated_hours": rec["estimated_hours"],
            "status": "blocked" if rec["blocked"] else "ok"
        })
    return suggestions
