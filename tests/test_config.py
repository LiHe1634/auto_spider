from pathlib import Path

import pytest

from auto_spider.config import CrawlerConfig, ConfigManager


def test_config_manager_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "crawlers.json"
    manager = ConfigManager(path)

    config = CrawlerConfig(name="demo", start_url="https://example.com", pattern="demo")
    manager.add_config(config)

    loaded = manager.get_config("demo")
    assert loaded == config

    configs = manager.list_configs()
    assert len(configs) == 1

    assert manager.remove_config("demo")
    assert manager.list_configs() == []


def test_config_manager_overwrite(tmp_path: Path) -> None:
    path = tmp_path / "crawlers.json"
    manager = ConfigManager(path)

    config1 = CrawlerConfig(name="demo", start_url="https://a", pattern="x")
    config2 = CrawlerConfig(name="demo", start_url="https://b", pattern="y")

    manager.add_config(config1)

    with pytest.raises(ValueError):
        manager.add_config(config2)

    manager.add_config(config2, overwrite=True)
    assert manager.get_config("demo") == config2
