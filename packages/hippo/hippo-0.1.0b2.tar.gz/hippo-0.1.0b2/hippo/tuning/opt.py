"""Optuna-powered hyperparameter search."""
from __future__ import annotations

from typing import Callable, Dict, Tuple

import optuna
from optuna import Trial
from sklearn.model_selection import cross_val_score


def optimise(
    objective_builder: Callable[[Trial], Tuple],
    n_trials: int = 50,
    direction: str = "maximize",
    study_name: str | None = None,
    storage: str | None = None,
) -> optuna.Study:
    """Run Optuna optimisation on the provided objective builder.

    `objective_builder` must return a function that Optuna can call,
    wrapping pipeline + cross-validation logic.
    """
    study = optuna.create_study(direction=direction, study_name=study_name, storage=storage)

    study.optimize(objective_builder, n_trials=n_trials, showcalls=False)
    return study