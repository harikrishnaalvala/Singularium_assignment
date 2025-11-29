"""
Config service for application layer.

This module encapsulates configuration merging and defaulting logic.
It provides an easy way to supply user overrides to the scoring engine.

Inputs:
- optional overrides mapping from request

Outputs:
- resolved config mapping to be consumed by domain scoring engine
"""

from typing import Dict
from copy import deepcopy
from dataclasses import asdict

from core.scoring.scoring_config import ScoringConfig

_DEFAULT_SCORING_CFG = ScoringConfig()

_SCORING_DEFAULTS = asdict(_DEFAULT_SCORING_CFG)

DEFAULT_APP_CONFIG: Dict = {
    # scoring-related defaults (must align with ScoringConfig fields)
    **_SCORING_DEFAULTS,
    # additional application-level toggles
    "default_estimated_hours": 4.0,
    "min_importance": 1,
    "max_importance": 10,
    "far_future_days": 3650,
    "enable_eisenhower": False,
    "q_multipliers": {
        "Q1_TOP": 1.3,
        "Q2_URGENT": 1.1,
        "Q3_IMPORTANT": 1.0,
        "Q4_LOW": 0.9
    }
}


def merge_config(overrides: Dict) -> Dict:
    """
    Merge default configuration with overrides provided by user.

    Inputs:
        overrides: mapping with zero or more keys that match default config keys

    Output:
        resolved config mapping

    Behavior:
        - deep copy of defaults is created to avoid mutation
        - overrides shallowly applied
        - nested structures are shallow-merged where needed
    """
    cfg = deepcopy(DEFAULT_APP_CONFIG)
    if not overrides:
        return cfg
    # merge top level
    for k, v in overrides.items():
        if k == "q_multipliers" and isinstance(v, dict):
            cfg["q_multipliers"].update(v)
        else:
            cfg[k] = v
    return cfg


def build_scoring_config(cfg: Dict) -> ScoringConfig:
    """Convert merged config mapping into ScoringConfig dataclass."""

    scoring_values = asdict(_DEFAULT_SCORING_CFG)
    for field in scoring_values:
        if field in cfg:
            scoring_values[field] = cfg[field]
    return ScoringConfig(**scoring_values)
