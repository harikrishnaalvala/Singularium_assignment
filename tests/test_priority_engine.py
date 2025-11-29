from datetime import date, timedelta

from django.test import SimpleTestCase

from application.services.config_service import build_scoring_config, merge_config
from core.models.dependency_graph import DependencyGraph
from core.models.task_entity import TaskEntity
from core.scoring.priority_engine import PriorityEngine
from core.validators.task_validator import TaskValidator


def _make_task(task_id: str, due_days: int = 1, hours: float = 2.0, importance: int = 5, deps=None) -> TaskEntity:
    """Helper to build TaskEntity instances for tests."""

    deps = deps or []
    return TaskEntity(
        id=task_id,
        title=f"Task {task_id}",
        due_date=date.today() + timedelta(days=due_days),
        estimated_hours=hours,
        importance=importance,
        dependencies=deps,
    )


class TaskValidatorTests(SimpleTestCase):
    def test_validator_accepts_normal_task(self) -> None:
        validator = TaskValidator()
        task = _make_task("t1")
        ok, issues = validator.validate(task)
        self.assertTrue(ok)
        self.assertEqual(issues, [])

    def test_validator_flags_missing_fields(self) -> None:
        broken = TaskEntity(
            id=None,
            title=" ",
            due_date=None,
            estimated_hours=0,
            importance=-1,
            dependencies="not-a-list",  # type: ignore[arg-type]
        )
        validator = TaskValidator()
        ok, issues = validator.validate(broken)
        self.assertFalse(ok)
        fields = {issue["field"] for issue in issues}
        self.assertTrue({"title", "due_date", "estimated_hours", "importance", "dependencies"}.issubset(fields))


class DependencyGraphTests(SimpleTestCase):
    def test_cycle_detection_and_stack_cleanup(self) -> None:
        task_a = _make_task("A", deps=["B"])
        task_b = _make_task("B", deps=["C"])
        task_c = _make_task("C", deps=["A"])
        graph = DependencyGraph({t.id: t for t in [task_a, task_b, task_c]})
        self.assertTrue(graph.has_cycle())
        cycles = graph.get_cycles()
        self.assertTrue(any(set(cycle) == {"A", "B", "C"} for cycle in cycles))

        task_c.dependencies = []
        graph2 = DependencyGraph({t.id: t for t in [task_a, task_b, task_c]})
        self.assertFalse(graph2.has_cycle())


class ConfigAdapterTests(SimpleTestCase):
    def test_build_scoring_config_respects_overrides(self) -> None:
        overrides = {"weight_urgency": 2.5, "urgency_mode": "threshold"}
        merged = merge_config(overrides)
        scoring_cfg = build_scoring_config(merged)
        self.assertEqual(merged["weight_urgency"], 2.5)
        self.assertEqual(scoring_cfg.weight_urgency, 2.5)
        self.assertEqual(scoring_cfg.urgency_mode, "threshold")


class PriorityEngineTests(SimpleTestCase):
    def test_priority_engine_prefers_high_urgency(self) -> None:
        tasks = [_make_task("A", due_days=0, hours=1), _make_task("B", due_days=5, hours=5)]
        config_dict = merge_config({"weight_importance": 2.0})
        scoring_config = build_scoring_config(config_dict)
        engine = PriorityEngine(scoring_config)
        scores = engine.score_tasks(tasks)
        self.assertEqual(scores[0][0].id, "A")
