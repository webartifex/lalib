"""Generic utilities for the library."""

from typing import Any


try:
    from typing import Self
except ImportError:  # pragma: no cover to support Python 3.9 & 3.10
    from typing_extensions import Self


class SingletonMixin:
    """Utility class to provide singleton pattern implementation."""

    _instance: Self

    @staticmethod
    def __new__(cls: type[Self], *args: Any, **kwargs: Any) -> Self:
        """Check if the `_instance` already exists."""
        if getattr(cls, "_instance", None) is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
