"""Data models used throughout the project."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass(slots=True)
class SpiderConfig:
    """Configuration for a single spider instance."""

    name: str
    start_url: str
    parser: str
    schedule: Dict[str, Any] | None = None
    enabled: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the configuration to a JSON compatible dictionary."""

        return {
            "name": self.name,
            "start_url": self.start_url,
            "parser": self.parser,
            "schedule": self.schedule,
            "enabled": self.enabled,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpiderConfig":
        """Create an instance from a plain dictionary."""

        return cls(
            name=data["name"],
            start_url=data["start_url"],
            parser=data.get("parser", "title"),
            schedule=data.get("schedule"),
            enabled=data.get("enabled", True),
            extra=dict(data.get("extra", {})),
        )


@dataclass(slots=True)
class SpiderResult:
    """Result returned after running a spider."""

    name: str
    url: str
    fetched_at: datetime
    data: Any

    @classmethod
    def create(cls, name: str, url: str, data: Any) -> "SpiderResult":
        """Convenience constructor filling the timestamp automatically."""

        return cls(name=name, url=url, fetched_at=datetime.now(timezone.utc), data=data)
