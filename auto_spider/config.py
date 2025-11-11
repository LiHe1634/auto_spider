"""配置管理模块。

负责加载与保存爬虫配置。配置使用 JSON 文件持久化，每个爬虫
包含名称、起始 URL、匹配规则以及可选描述。
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_DATA_DIR = Path("data")
DEFAULT_CONFIG_PATH = DEFAULT_DATA_DIR / "crawlers.json"


@dataclass
class CrawlerConfig:
    """表示单个爬虫的配置。"""

    name: str
    start_url: str
    pattern: str
    description: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "CrawlerConfig":
        return cls(
            name=data["name"],
            start_url=data["start_url"],
            pattern=data["pattern"],
            description=data.get("description", ""),
        )

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class ConfigManager:
    """读写爬虫配置文件的帮助类。"""

    def __init__(self, path: Path = DEFAULT_CONFIG_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write_configs([])

    def list_configs(self) -> List[CrawlerConfig]:
        raw = self._read_configs()
        return [CrawlerConfig.from_dict(item) for item in raw]

    def get_config(self, name: str) -> Optional[CrawlerConfig]:
        for config in self.list_configs():
            if config.name == name:
                return config
        return None

    def add_config(self, config: CrawlerConfig, overwrite: bool = False) -> None:
        configs = self.list_configs()
        for idx, existing in enumerate(configs):
            if existing.name == config.name:
                if not overwrite:
                    raise ValueError(f"配置 {config.name} 已存在，若需覆盖请设置 overwrite=True")
                configs[idx] = config
                self._write_configs(configs)
                return
        configs.append(config)
        self._write_configs(configs)

    def remove_config(self, name: str) -> bool:
        configs = self.list_configs()
        new_configs = [cfg for cfg in configs if cfg.name != name]
        if len(new_configs) == len(configs):
            return False
        self._write_configs(new_configs)
        return True

    # 内部工具方法
    def _read_configs(self) -> List[Dict[str, str]]:
        with self.path.open("r", encoding="utf-8") as fp:
            try:
                data = json.load(fp)
            except json.JSONDecodeError:
                raise ValueError(f"配置文件 {self.path} 格式错误，无法解析")
        if not isinstance(data, list):
            raise ValueError("配置文件格式应为包含多个配置的列表")
        return data

    def _write_configs(self, configs: List[CrawlerConfig]) -> None:
        serializable = [cfg.to_dict() if isinstance(cfg, CrawlerConfig) else cfg for cfg in configs]
        with self.path.open("w", encoding="utf-8") as fp:
            json.dump(serializable, fp, ensure_ascii=False, indent=2)
