"""PeekPy - A Python framework for building web applications.
This module provides a decorator for analyzing function performance and usage statistics.
"""

import time

from peekpy.config.settings import is_enabled
from peekpy.storage import stats_manager


def analyze(_func=None, *, count: bool = True, time_measure: bool = False):
    """Decorator to analyze function performance and usage statistics.
    Args:
        _func (callable, optional): The function to be decorated. Defaults to None.
        count (bool, optional): Whether to count the number of times the function is called.
        Defaults to True.
        time_measure (bool, optional): Whether to measure the execution time of the function.
        Defaults to False.
    Returns:
        callable: The decorated function with performance and usage statistics.
    """

    def decorator(func):
        """Decorator function to wrap the original function."""

        def wrapper(*args, **kwargs):
            """Wrapper function to analyze the performance and usage of the original function."""
            if not is_enabled():
                return func(*args, **kwargs)

            if count:
                stats_manager.increment_stat(func.__name__)
            if time_measure:
                start = time.perf_counter()
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                stats_manager.add_time(func.__name__, elapsed)
                return result

            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)
