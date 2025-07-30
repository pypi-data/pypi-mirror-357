"""PeekPy package initialization module."""

from peekpy.core.analyse import analyze
from peekpy.config.settings import is_enabled, enable, disable
from peekpy.storage import stats_manager
from peekpy.storage.stats_manager import get_stats

__all__ = ["analyze", "is_enabled", "enable", "disable", "stats_manager", "get_stats"]
