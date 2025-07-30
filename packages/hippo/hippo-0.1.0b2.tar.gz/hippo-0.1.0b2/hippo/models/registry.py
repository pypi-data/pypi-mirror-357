"""Factory for ML models with sane defaults."""
from __future__ import annotations

from typing import Any, Dict

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier  # optional dependency

_MODEL_MAP = {
    "rf": RandomForestClassifier,
    "xgb": XGBClassifier,
}


def get_model(name: str, **kwargs: Dict[str, Any]):
    """Return a fresh model instance by key."""
    if name not in _MODEL_MAP:
        raise KeyError(f"Unknown model {name!r}. Choices: {list(_MODEL_MAP)}")
    return _MODEL_MAP[name](**kwargs)
