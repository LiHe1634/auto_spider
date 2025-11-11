from __future__ import annotations

import json
from pathlib import Path

import pytest

from auto_spider.config_store import ConfigStore
from auto_spider.exceptions import ConfigDataError
from auto_spider.models import SpiderConfig


def test_load_empty_when_file_missing(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "spiders.json")
    assert store.load() == []


def test_save_and_reload(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "spiders.json")
    config = SpiderConfig(name="example", start_url="https://example.com", parser="title")
    store.save([config])
    loaded = store.load()
    assert len(loaded) == 1
    assert loaded[0].name == "example"


def test_invalid_json_raises(tmp_path: Path) -> None:
    path = tmp_path / "spiders.json"
    path.write_text("not json", encoding="utf-8")
    store = ConfigStore(path)
    with pytest.raises(ConfigDataError):
        store.load()


def test_non_list_json_raises(tmp_path: Path) -> None:
    path = tmp_path / "spiders.json"
    path.write_text(json.dumps({"invalid": True}), encoding="utf-8")
    store = ConfigStore(path)
    with pytest.raises(ConfigDataError):
        store.load()
