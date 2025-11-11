"""Core package for the :mod:`auto_spider` project."""

from .manager import SpiderManager
from .models import SpiderConfig, SpiderResult
from .parsers import ParserRegistry
from .config_store import ConfigStore
from .exceptions import (
    SpiderError,
    SpiderConfigError,
    SpiderNotFoundError,
    SpiderDisabledError,
    ParserNotFoundError,
    ConfigDataError,
)

__all__ = [
    "SpiderManager",
    "SpiderConfig",
    "SpiderResult",
    "ParserRegistry",
    "ConfigStore",
    "SpiderError",
    "SpiderConfigError",
    "SpiderNotFoundError",
    "SpiderDisabledError",
    "ParserNotFoundError",
    "ConfigDataError",
]
