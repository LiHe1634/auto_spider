"""Spider implementations."""

from __future__ import annotations

import contextlib
import urllib.request
from typing import Optional

from .exceptions import ParserNotFoundError, SpiderError
from .models import SpiderConfig, SpiderResult
from .parsers import ParserRegistry


class Spider:
    """Base spider implementation."""

    def __init__(self, config: SpiderConfig, registry: ParserRegistry | None = None) -> None:
        self.config = config
        self.registry = registry or ParserRegistry()

    def fetch(self) -> str:  # pragma: no cover - abstract method
        raise NotImplementedError

    def parse(self, html: str) -> SpiderResult:
        parser = self.registry.get(self.config.parser)
        if parser is None:
            raise ParserNotFoundError(f"Parser '{self.config.parser}' is not registered")
        data = parser(html, self.config)
        return SpiderResult.create(self.config.name, self.config.start_url, data)

    def run(self) -> SpiderResult:
        html = self.fetch()
        return self.parse(html)


class HttpSpider(Spider):
    """Concrete spider that performs HTTP requests using the standard library."""

    def __init__(
        self,
        config: SpiderConfig,
        registry: ParserRegistry | None = None,
        *,
        timeout: Optional[float] = 10.0,
        user_agent: str = "auto-spider/1.0",
    ) -> None:
        super().__init__(config, registry)
        self.timeout = timeout
        self.user_agent = user_agent

    def fetch(self) -> str:
        request = urllib.request.Request(
            self.config.start_url,
            headers={"User-Agent": self.user_agent},
        )
        try:
            with contextlib.closing(urllib.request.urlopen(request, timeout=self.timeout)) as response:
                raw = response.read()
                encoding = response.headers.get_content_charset() or "utf-8"
        except OSError as exc:  # pragma: no cover - network errors are unlikely in tests
            raise SpiderError(f"Failed to fetch '{self.config.start_url}': {exc}") from exc
        return raw.decode(encoding, errors="replace")
