"""抓取结果存储模块。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .crawler import CrawlResult

DEFAULT_RESULTS_DIR = Path("data") / "results"


class ResultStorage:
    """负责持久化爬虫运行结果。"""

    def __init__(self, directory: Path = DEFAULT_RESULTS_DIR) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, result: CrawlResult) -> Path:
        timestamp = result.fetched_at.strftime("%Y%m%d%H%M%S")
        filename = f"{result.name}_{timestamp}.json"
        path = self.directory / filename
        data = self._serialize_result(result)
        with path.open("w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        return path

    def list_results(self, name: str | None = None) -> List[Path]:
        files = sorted(self.directory.glob("*.json"))
        if name:
            prefix = f"{name}_"
            files = [f for f in files if f.name.startswith(prefix)]
        return files

    def load(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)

    def load_latest(self, name: str) -> Dict[str, Any] | None:
        results = self.list_results(name)
        if not results:
            return None
        return self.load(results[-1])

    @staticmethod
    def _serialize_result(result: CrawlResult) -> Dict[str, Any]:
        return {
            "name": result.name,
            "url": result.url,
            "status": result.status,
            "matches": result.matches,
            "error": result.error,
            "fetched_at": result.fetched_at.isoformat(),
        }

    @staticmethod
    def export(results: Iterable[CrawlResult], path: Path) -> Path:
        data = [ResultStorage._serialize_result(res) for res in results]
        with path.open("w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        return path
