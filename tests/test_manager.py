from __future__ import annotations

import pytest

from auto_spider.config_store import ConfigStore
from auto_spider.exceptions import SpiderConfigError, SpiderDisabledError, SpiderNotFoundError
from auto_spider.manager import SpiderFactory, SpiderManager
from auto_spider.models import SpiderConfig, SpiderResult
from auto_spider.parsers import ParserRegistry
from auto_spider.spider import Spider


class _FakeSpider(Spider):
    def __init__(self, config: SpiderConfig, html: str, registry: ParserRegistry | None = None) -> None:
        super().__init__(config, registry)
        self.html = html

    def fetch(self) -> str:
        return self.html


class _FakeFactory(SpiderFactory):
    def __init__(self, html: str) -> None:
        super().__init__(ParserRegistry())
        self.html = html

    def create(self, config: SpiderConfig) -> Spider:
        return _FakeSpider(config, self.html, self.registry)


@pytest.fixture()
def manager(tmp_path):
    store = ConfigStore(tmp_path / "spiders.json")
    factory = _FakeFactory("<html><head><title>Hello</title></head><body><a href='https://a'>A</a></body></html>")
    return SpiderManager(store=store, factory=factory)


def create_config(name: str = "example", enabled: bool = True) -> SpiderConfig:
    return SpiderConfig(name=name, start_url="https://example.com", parser="title", enabled=enabled)


def test_add_and_list(manager: SpiderManager) -> None:
    manager.add_spider(create_config("first"))
    manager.add_spider(create_config("second"))
    names = [config.name for config in manager.list_spiders()]
    assert names == ["first", "second"]


def test_add_duplicate_raises(manager: SpiderManager) -> None:
    manager.add_spider(create_config())
    with pytest.raises(SpiderConfigError):
        manager.add_spider(create_config())


def test_update_missing_raises(manager: SpiderManager) -> None:
    with pytest.raises(SpiderNotFoundError):
        manager.update_spider(create_config())


def test_update_existing(manager: SpiderManager) -> None:
    manager.add_spider(create_config())
    updated = SpiderConfig(name="example", start_url="https://changed", parser="links")
    manager.update_spider(updated)
    config = manager.get_spider("example")
    assert config.start_url == "https://changed"
    assert config.parser == "links"


def test_remove(manager: SpiderManager) -> None:
    manager.add_spider(create_config())
    manager.remove_spider("example")
    with pytest.raises(SpiderNotFoundError):
        manager.get_spider("example")


def test_remove_missing_raises(manager: SpiderManager) -> None:
    with pytest.raises(SpiderNotFoundError):
        manager.remove_spider("example")


def test_run_spider(manager: SpiderManager) -> None:
    manager.add_spider(create_config())
    result = manager.run_spider("example")
    assert isinstance(result, SpiderResult)
    assert result.data["title"] == "Hello"


def test_run_disabled_spider(manager: SpiderManager) -> None:
    manager.add_spider(create_config(enabled=False))
    with pytest.raises(SpiderDisabledError):
        manager.run_spider("example")
