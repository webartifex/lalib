"""Utilities to test the `lalib` package."""

from lalib import config


DEFAULT_THRESHOLD = config.THRESHOLD
WITHIN_THRESHOLD = config.THRESHOLD / 10
NOT_WITHIN_THRESHOLD = config.THRESHOLD * 10
