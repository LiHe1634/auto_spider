"""爬虫执行逻辑。"""

from __future__ import annotations

import re
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .config import CrawlerConfig


@dataclass
class CrawlResult:
    """保存单次爬取的结果信息。"""

    name: str
    fetched_at: datetime
    status: str
    matches: List[str]
    error: Optional[str] = None
    url: Optional[str] = None

    def summary(self) -> str:
        if self.error:
            return f"[{self.name}] 失败: {self.error}"
        preview = ", ".join(self.matches[:3])
        if len(self.matches) > 3:
            preview += " ..."
        return f"[{self.name}] 成功匹配 {len(self.matches)} 项: {preview}"


class SpiderRunner:
    """根据配置抓取网页并匹配结果。"""

    def __init__(self, *, user_agent: str | None = None, timeout: int = 10) -> None:
        self.user_agent = user_agent or (
            "Mozilla/5.0 (X11; Linux x86_64) AutoSpider/1.0"
        )
        self.timeout = timeout

    def run(self, config: CrawlerConfig) -> CrawlResult:
        request = urllib.request.Request(
            config.start_url,
            headers={"User-Agent": self.user_agent},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as resp:
                encoding = resp.headers.get_content_charset("utf-8")
                body = resp.read().decode(encoding, errors="ignore")
        except Exception as exc:  # pragma: no cover - 网络异常行为多样
            return CrawlResult(
                name=config.name,
                fetched_at=datetime.utcnow(),
                status="failed",
                matches=[],
                error=str(exc),
                url=config.start_url,
            )

        pattern = re.compile(config.pattern)
        matches = pattern.findall(body)
        matches = [match if isinstance(match, str) else "".join(match) for match in matches]

        return CrawlResult(
            name=config.name,
            fetched_at=datetime.utcnow(),
            status="success",
            matches=matches,
            url=config.start_url,
        )
