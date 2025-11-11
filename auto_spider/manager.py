"""High level interface for managing spiders."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

from .config_store import ConfigStore
from .exceptions import SpiderConfigError, SpiderDisabledError, SpiderNotFoundError
from .models import SpiderConfig, SpiderResult
from .parsers import ParserRegistry
from .spider import HttpSpider, Spider


class SpiderFactory:
    """Factory responsible for creating spider instances."""

    def __init__(self, registry: ParserRegistry | None = None) -> None:
        self.registry = registry or ParserRegistry()

    def create(self, config: SpiderConfig) -> Spider:
        return HttpSpider(config, self.registry)


class SpiderManager:
    """Manage spider configurations and execution."""

    def __init__(
        self,
        store: ConfigStore | None = None,
        *,
        config_path: str | Path | None = None,
        factory: SpiderFactory | None = None,
    ) -> None:
        if store is None:
            path = Path(config_path) if config_path is not None else Path("spiders.json")
            store = ConfigStore(path)
        self._store = store
        self._factory = factory or SpiderFactory()

    @property
    def store(self) -> ConfigStore:
        return self._store

    def list_spiders(self) -> Sequence[SpiderConfig]:
        return tuple(self._store.load())

    def add_spider(self, config: SpiderConfig) -> None:
        if self._store.find(config.name) is not None:
            raise SpiderConfigError(f"Spider '{config.name}' already exists")
        self._store.upsert(config)

    def update_spider(self, config: SpiderConfig) -> None:
        if self._store.find(config.name) is None:
            raise SpiderNotFoundError(f"Spider '{config.name}' does not exist")
        self._store.upsert(config)

    def remove_spider(self, name: str) -> None:
        if not self._store.delete(name):
            raise SpiderNotFoundError(f"Spider '{name}' does not exist")

    def get_spider(self, name: str) -> SpiderConfig:
        config = self._store.find(name)
        if config is None:
            raise SpiderNotFoundError(f"Spider '{name}' does not exist")
        return config

    def run_spider(self, name: str) -> SpiderResult:
        config = self.get_spider(name)
        if not config.enabled:
            raise SpiderDisabledError(f"Spider '{name}' is disabled")
        spider = self._factory.create(config)
        return spider.run()

    def upsert_many(self, configs: Iterable[SpiderConfig]) -> None:
        incoming = list(configs)
        incoming_names = [config.name for config in incoming]
        if len(set(incoming_names)) != len(incoming_names):
            raise SpiderConfigError("Duplicate spider names provided in input")

        existing_configs = self._store.load()
        existing = {config.name for config in existing_configs}
        duplicate = existing.intersection(incoming_names)
        if duplicate:
            raise SpiderConfigError(
                "Cannot upsert multiple spiders when duplicates already exist: "
                + ", ".join(sorted(duplicate))
            )
        all_configs: List[SpiderConfig] = list(existing_configs) + incoming
        self._store.save(all_configs)
