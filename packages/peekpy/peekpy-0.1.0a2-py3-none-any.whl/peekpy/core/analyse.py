"""PeekPy - A Python framework for building web applications.
This module provides a decorator for analyzing function performance and usage statistics.
"""

from peekpy.config.settings import is_enabled
from peekpy.core.analyzers import CallCounter


def analyze(_func=None, *, analyzers=None):
    """ Decorator to analyze the performance and usage of a function."""
    if analyzers is None:
        analyzers = [CallCounter()]

    def decorator(func):
        """Decorator function to wrap the original function."""

        def wrapper(*args, **kwargs):
            """Wrapper function to analyze the performance and usage of the original function."""
            if not is_enabled():
                return func(*args, **kwargs)

            for analyzer in analyzers:
                analyzer.before(func, *args, **kwargs)

            result = func(*args, **kwargs)

            for analyzer in analyzers:
                analyzer.after(func, result, *args, **kwargs)

            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)
