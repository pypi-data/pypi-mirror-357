"""Rewire strategies for modifying and updating project connections and dependencies."""

from .strategy_registry import get_strategies_dict

__all__ = ["get_strategies_dict"]
