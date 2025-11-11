"""auto_spider 包提供一个可配置、可管理的小型爬虫系统。"""

from .config import CrawlerConfig, ConfigManager
from .crawler import SpiderRunner, CrawlResult
from .storage import ResultStorage

__all__ = [
    "CrawlerConfig",
    "ConfigManager",
    "SpiderRunner",
    "CrawlResult",
    "ResultStorage",
]
