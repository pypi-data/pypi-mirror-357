"""Stats Manager for tracking function call statistics.
This module provides functionality to increment statistics for function calls,
add execution time, and save statistics to a file.
"""

import json


class StatsManager:
    """Class to manage function call statistics."""

    def __init__(self):
        self._stats = {}

    def increment_stat(self, func_name: str, key: str = "calls_count", value: int = 1):
        """Increment the statistic for a function call.
        Args:
            func_name (str): The name of the function.
            key (str, optional): The key for the statistic. Defaults to "calls_count".
            value (int, optional): The value to increment. Defaults to 1.
        """
        if func_name not in self._stats:
            self._stats[func_name] = {}
        self._stats[func_name][key] = self._stats[func_name].get(key, 0) + value

    def add_time(self, func_name, elapsed):
        """Add execution time for a function call.
        Args:
            func_name (str): The name of the function.
            elapsed (float): The elapsed time for the function call in seconds.
        """
        if func_name not in self._stats:
            self._stats[func_name] = {}
        if "times" not in self._stats[func_name]:
            self._stats[func_name]["times"] = []
        self._stats[func_name]["times"].append(elapsed)

    def get_stats(self):
        """Get the current statistics for function calls.
        Returns:
            dict: A dictionary containing the statistics for function calls.
        """
        return self._stats

    def reset_stats(self):
        """Reset the statistics for function calls."""
        self._stats = {}


stats_manager = StatsManager()


def get_stats():
    """Get the current statistics for function calls.
    Returns:
        dict: A dictionary containing the statistics for function calls.
    """
    return stats_manager.get_stats()


def reset_stats():
    """Reset the statistics for function calls."""
    stats_manager.reset_stats()


def save_stats_to_file(file_path: str):
    """Save the current statistics to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(stats_manager.get_stats, file, indent=4)
