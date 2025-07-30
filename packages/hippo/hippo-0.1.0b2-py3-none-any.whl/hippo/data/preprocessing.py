"""Declarative preprocessing pipelines."""
from __future__ import annotations

from typing import List

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def build_pipeline(
    num_feats: List[str],
    cat_feats: List[str],
    scaler: str = "standard",
    impute_strategy: str = "median",
) -> ColumnTransformer:
    """Return a sklearn ColumnTransformer with sensible defaults.

    Parameters
    ----------
    num_feats : list[str]
        Numerical feature names.
    cat_feats : list[str]
        Categorical feature names.
    scaler : {"standard", "none"}
        How to scale numerical features.
    impute_strategy : {"mean", "median", "most_frequent"}
        Strategy for imputing missing values.
    """
    num_pipe = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy=impute_strategy)),
            ("scale", StandardScaler() if scaler == "standard" else "passthrough"),
        ],
    )
    cat_pipe = Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore")),
        ],
    )
    return ColumnTransformer(
        transformers=[("num", num_pipe, num_feats), ("cat", cat_pipe, cat_feats)]
    )
