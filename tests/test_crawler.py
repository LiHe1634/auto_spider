from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from auto_spider.config import CrawlerConfig
from auto_spider.crawler import SpiderRunner


class FakeResponse:
    def __init__(self, data: str, encoding: str = "utf-8") -> None:
        self._data = data.encode(encoding)
        self.headers = SimpleNamespace(get_content_charset=lambda default: encoding)

    def read(self) -> bytes:  # pragma: no cover - 简单封装
        return self._data

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_spider_runner_success() -> None:
    html = "<html><body><h1>News 123</h1><p>News 456</p></body></html>"
    config = CrawlerConfig(name="news", start_url="https://example.com", pattern=r"News (\d+)")
    runner = SpiderRunner()

    with patch("urllib.request.urlopen", return_value=FakeResponse(html)):
        result = runner.run(config)

    assert result.status == "success"
    assert result.matches == ["123", "456"]


def test_spider_runner_failure() -> None:
    config = CrawlerConfig(name="news", start_url="https://example.com", pattern=".")
    runner = SpiderRunner()

    with patch("urllib.request.urlopen", side_effect=RuntimeError("network")):
        result = runner.run(config)

    assert result.status == "failed"
    assert result.error == "network"
