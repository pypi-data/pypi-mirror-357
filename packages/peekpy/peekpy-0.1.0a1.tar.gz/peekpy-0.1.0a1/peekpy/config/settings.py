"""Settings for PeekPy configuration."""


class Settings:
    """Class to manage PeekPy settings."""

    def __init__(self):
        self._enabled = False

    def enable(self):
        """Enable PeekPy functionality."""
        self._enabled = True

    def disable(self):
        """Disable PeekPy functionality."""
        self._enabled = False

    def is_enabled(self):
        """Check if PeekPy functionality is enabled."""
        return self._enabled


settings = Settings()


def enable():
    """Enable PeekPy functionality."""
    settings.enable()


def disable():
    """Disable PeekPy functionality."""
    settings.disable()


def is_enabled():
    """Check if PeekPy functionality is enabled."""
    return settings.is_enabled()
