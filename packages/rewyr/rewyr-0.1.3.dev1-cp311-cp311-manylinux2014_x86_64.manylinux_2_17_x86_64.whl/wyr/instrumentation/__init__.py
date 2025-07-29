"""Instrumentation package for monitoring LLM calls."""

from .injector import inject_instrumentation
from .patch import WyrInstrumentator

__all__ = ["WyrInstrumentator", "inject_instrumentation"]
