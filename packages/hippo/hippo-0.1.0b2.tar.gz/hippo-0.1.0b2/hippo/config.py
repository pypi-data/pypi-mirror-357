"""Global configuration & dataclass helpers."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

CFG_FILE = Path.home() / ".hippo" / "config.toml"


@dataclass
class SearchSpace:
    """Hyperparameter search space description."""
    params: Dict[str, Any] = field(default_factory=dict)
    n_trials: int = 50
    direction: str = "minimize"         # e.g. loss

