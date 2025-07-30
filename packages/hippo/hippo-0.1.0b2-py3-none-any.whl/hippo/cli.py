"""Simple CLI: `python -m hippo.cli train config.yml`."""
import json
import sys
from pathlib import Path

import joblib
import yaml
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from hippo.data.preprocessing import build_pipeline
from hippo.models.registry import get_model
from hippo.tracking.tracker import Tracker


def _load_cfg(cfg_path: Path) -> dict:
    with cfg_path.open() as fp:
        return yaml.safe_load(fp)


def train(cfg_file: str | Path):
    """Train pipeline from YAML config."""
    cfg = _load_cfg(Path(cfg_file))

    # 1. Load data (CSV for demo)
    df = joblib.load(cfg["data"]["path"])
    y = df[cfg["data"]["target"]]
    X = df.drop(columns=[cfg["data"]["target"]])

    num_cols = cfg["data"]["numerical"]
    cat_cols = cfg["data"]["categorical"]

    pipe = build_pipeline(num_cols, cat_cols)

    model = get_model(cfg["model"]["name"], **cfg["model"].get("params", {}))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with Tracker(cfg["run_name"]).start() as (log_metric, log_param):
        model.fit(pipe.fit_transform(X_train), y_train)

        preds = model.predict(pipe.transform(X_test))
        acc = accuracy_score(y_test, preds)
        log_metric("accuracy", acc)
        log_param("model", cfg["model"]["name"])

    print(f"✅ accuracy={acc:.4f}")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "train":
        sys.exit("Usage: python -m hippo.cli train <config.yml>")
    train(sys.argv[2])