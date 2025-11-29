"""
Application service that orchestrates task analysis.

Responsibilities:
- convert raw payload tasks into DTOs
- validate minimal invariants
- detect dependency cycles
- run domain scoring engine
- format results for API layer

Inputs:
- tasks_payload: list of raw task dicts
- config_overrides: optional mapping to alter scoring behavior
- domain components: validators, date parser, scoring engine instance

Outputs:
- list of enriched task dicts sorted by computed score
- warnings list describing any issues found during processing
"""

from typing import List, Dict, Tuple
from datetime import date, datetime, timedelta

from application.dto.task_dto import to_task_dto, TaskDTO
from application.services.config_service import merge_config, build_scoring_config

# domain imports (pure domain layer). These must be implemented in core.scoring modules.
from core.models.dependency_graph import DependencyGraph
from core.scoring.priority_engine import PriorityEngine
from core.validators.task_validator import TaskValidator


def _date_parser(raw_date):
    """
    Simple date parser used by DTO conversion.

    Inputs:
        raw_date: string or None

    Outputs:
        datetime.date object; falls back to far future date on parse failure
    """
    if not raw_date:
        return date.today() + timedelta(days=3650)
    try:
        # attempt ISO parse then common patterns
        return datetime.fromisoformat(raw_date).date()
    except Exception:
        try:
            return datetime.strptime(raw_date, "%Y-%m-%d").date()
        except Exception:
            return date.today() + timedelta(days=3650)


def _validate_and_collect(dtos: List[TaskDTO]) -> Tuple[List[TaskDTO], List[Dict]]:
    """
    Validate DTOs using domain validator and collect warnings.

    Inputs:
        dtos: list of TaskDTO instances

    Outputs:
        tuple(valid_dtos, warnings)

    Warnings are mappings with keys:
        - id or index
        - message
        - field (optional)
    """
    valid = []
    warnings = []
    validator = TaskValidator()
    for idx, dto in enumerate(dtos):
        ok, issues = validator.validate(dto)
        if ok:
            valid.append(dto)
        else:
            warnings.append({"id": dto.id or f"idx_{idx}", "issues": issues})
            # still include the dto so the user can fix it; mark dto via attribute
            dto.raw["_validation_issues"] = issues
            valid.append(dto)
    return valid, warnings


def _build_task_map(dtos: List[TaskDTO]) -> Dict[str, TaskDTO]:
    """
    Build mapping of id -> TaskDTO. If id is missing, use title as fallback.

    Inputs:
        dtos: list of TaskDTO

    Output:
        mapping where keys are str identifiers and values are TaskDTO
    """
    task_map = {}
    for t in dtos:
        key = t.id or t.title
        task_map[str(key)] = t
    return task_map


def analyze_tasks_service(tasks_payload: List[Dict], config_overrides: Dict = None) -> Dict:
    """
    Main application entrypoint for analyze use case.

    Inputs:
        tasks_payload: list of raw task dicts from client
        config_overrides: optional mapping to modify scoring parameters

    Outputs:
        result mapping containing:
            - priority_list: list of enriched tasks sorted by score
            - blocked_tasks: list of tasks part of cycles
            - needs_attention: list of tasks with validation warnings
            - warnings: list of validation messages
            - config_used: resolved config mapping
    """
    config_dict = merge_config(config_overrides or {})
    scoring_config = build_scoring_config(config_dict)

    # convert raw tasks into DTOs
    dtos: List[TaskDTO] = [to_task_dto(raw, _date_parser) for raw in tasks_payload]

    # validate and collect warnings
    valid_dtos, warnings = _validate_and_collect(dtos)

    # dependency analysis
    task_map = _build_task_map(valid_dtos)
    dep_graph = DependencyGraph(task_map)
    cycles = dep_graph.get_cycles()
    blocked_ids = set()
    for cycle in cycles:
        for node in cycle:
            blocked_ids.add(node)

    # mark blocked tasks
    for tid, dto in task_map.items():
        if tid in blocked_ids:
            dto.raw["_blocked_by_cycle"] = True

    # scoring
    engine = PriorityEngine(scoring_config)
    scored_results = []
    for tid, dto in task_map.items():
        # convert dto into domain TaskEntity expected by engine
        # the PriorityEngine is expected to accept an object with attributes oriented as TaskEntity;
        # adapt or map fields if core expects different shape.
        score = engine.score_task(dto, task_map)
        explanation = engine.explain_task(dto, task_map) if hasattr(engine, "explain_task") else ""
        scored_results.append({
            "id": dto.id,
            "title": dto.title,
            "due_date": dto.due_date.isoformat(),
            "estimated_hours": dto.estimated_hours,
            "importance": dto.importance,
            "dependencies": dto.dependencies,
            "score": score,
            "explanation": explanation,
            "raw": dto.raw,
            "blocked": dto.raw.get("_blocked_by_cycle", False),
        })

    # sort by score descending, blocked tasks appended to blocked bucket
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    blocked_tasks = [r for r in scored_results if r["blocked"]]
    priority_list = [r for r in scored_results if not r["blocked"]]
    needs_attention = [r for r in scored_results if r["raw"].get("_validation_issues")]

    return {
        "priority_list": priority_list,
        "blocked_tasks": blocked_tasks,
        "needs_attention": needs_attention,
        "warnings": warnings,
        "config_used": config_dict
    }
