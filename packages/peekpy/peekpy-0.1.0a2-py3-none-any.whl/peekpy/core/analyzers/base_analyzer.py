""" Base class for analyzers in PeekPy.
This module defines the BaseAnalyzer class, which serves as a base for all analyzers in PeekPy."""

class BaseAnalyzer:
    """
    Base class for all analyzers in PeekPy.
    Analyzers should inherit from this class and implement the `analyze` method.
    """

    def before(self, func, *args, **kwargs):
        """
        Method to be called before the function execution.
        Can be overridden by subclasses to implement custom behavior.
        """

    def after(self, func, result, *args, **kwargs):
        """
        Method to be called after the function execution.
        Can be overridden by subclasses to implement custom behavior.
        """
