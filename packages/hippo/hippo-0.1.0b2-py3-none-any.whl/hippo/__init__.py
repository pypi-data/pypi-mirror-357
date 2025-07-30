"""Hierarchical Integrated Pre-processing & Parameter Optimisation."""
from importlib.metadata import version

from .data import preprocessing    # noqa: F401
from .models.registry import get_model  # noqa: F401
from .tuning.opt import optimise   # noqa: F401
from .tracking.tracker import Tracker  # noqa: F401

__all__ = ["preprocessing", "get_model", "optimise", "Tracker"]
__version__: str = version("hippo")