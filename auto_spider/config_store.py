"""Persistence layer for spider configuration."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Iterable, List

from .exceptions import ConfigDataError
from .models import SpiderConfig


class ConfigStore:
    """Simple JSON based configuration store."""

    def __init__(self, path: str | Path = "spiders.json") -> None:
        self._path = Path(path)
        self._lock = threading.RLock()

    @property
    def path(self) -> Path:
        """Return the path where the configuration is stored."""

        return self._path

    def load(self) -> List[SpiderConfig]:
        """Load all configurations from disk."""

        with self._lock:
            if not self._path.exists():
                return []
            try:
                text = self._path.read_text(encoding="utf-8")
            except OSError as exc:  # pragma: no cover - unlikely on tmpfs
                raise ConfigDataError(str(exc)) from exc
            if not text.strip():
                return []
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ConfigDataError("Invalid configuration file format") from exc
            if not isinstance(data, list):
                raise ConfigDataError("Configuration file must contain a list")
            return [SpiderConfig.from_dict(item) for item in data]

    def save(self, configs: Iterable[SpiderConfig]) -> None:
        """Persist the provided configurations to disk."""

        with self._lock:
            data = [config.to_dict() for config in configs]
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
            text = json.dumps(data, indent=2, ensure_ascii=False)
            tmp_path.write_text(text, encoding="utf-8")
            tmp_path.replace(self._path)

    def find(self, name: str) -> SpiderConfig | None:
        """Return the configuration with the given name if present."""

        for config in self.load():
            if config.name == name:
                return config
        return None

    def upsert(self, config: SpiderConfig) -> None:
        """Update or insert the provided configuration."""

        configs = self.load()
        for index, existing in enumerate(configs):
            if existing.name == config.name:
                configs[index] = config
                break
        else:
            configs.append(config)
        self.save(configs)

    def delete(self, name: str) -> bool:
        """Delete the configuration with the given name."""

        configs = self.load()
        filtered = [config for config in configs if config.name != name]
        if len(filtered) == len(configs):
            return False
        self.save(filtered)
        return True
