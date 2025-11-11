"""Custom exception hierarchy for the project."""

from __future__ import annotations


class SpiderError(RuntimeError):
    """Base class for all project specific errors."""


class SpiderConfigError(SpiderError):
    """Raised when a configuration related error occurs."""


class ConfigDataError(SpiderConfigError):
    """Raised when configuration data cannot be parsed."""


class SpiderNotFoundError(SpiderError):
    """Raised when attempting to access an unknown spider."""


class SpiderDisabledError(SpiderError):
    """Raised when attempting to run a disabled spider."""


class ParserNotFoundError(SpiderError):
    """Raised when a parser referenced by configuration is missing."""
