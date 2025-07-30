"""Stats Manager for tracking function call statistics.
"""

import json


class StatsManager:
    """Class to manage function call statistics."""

    def __init__(self):
        self._stats = {}

    def add_stats(self, func_name, stats: dict):
        """Add additional statistics for a function call.
        Args:
            func_name (str): The name of the function.
            stats (dict): A dictionary containing additional statistics to add.
        """
        stats = {func_name: stats}
        self._stats.update(stats)

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
        json.dump(stats_manager.get_stats(), file, indent=4)
