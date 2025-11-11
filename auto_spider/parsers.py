"""Built-in parsers and registry utilities."""

from __future__ import annotations

from html.parser import HTMLParser
from typing import Any, Callable, Dict, Iterable, List

from .models import SpiderConfig

Parser = Callable[[str, SpiderConfig], Any]


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self.result: List[str] = []

    def handle_starttag(self, tag: str, attrs: Iterable[tuple[str, str | None]]) -> None:  # pragma: no cover - html.parser internals
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:  # pragma: no cover - html.parser internals
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:  # pragma: no cover - html.parser internals
        if self._in_title:
            self.result.append(data.strip())

    def get_title(self) -> str:
        return " ".join(part for part in self.result if part)


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: List[str] = []

    def handle_starttag(self, tag: str, attrs: Iterable[tuple[str, str | None]]) -> None:  # pragma: no cover - html.parser internals
        if tag.lower() != "a":
            return
        for attr, value in attrs:
            if attr.lower() == "href" and value:
                self.links.append(value)


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._fragments: List[str] = []

    def handle_data(self, data: str) -> None:  # pragma: no cover - html.parser internals
        data = data.strip()
        if data:
            self._fragments.append(data)

    def get_text(self) -> str:
        return " ".join(self._fragments)


def parse_title(html: str, _: SpiderConfig) -> Dict[str, Any]:
    parser = _TitleParser()
    parser.feed(html)
    return {"title": parser.get_title()}


def parse_links(html: str, _: SpiderConfig) -> Dict[str, Any]:
    parser = _LinkParser()
    parser.feed(html)
    return {"links": parser.links}


def parse_text(html: str, _: SpiderConfig) -> Dict[str, Any]:
    parser = _TextParser()
    parser.feed(html)
    return {"text": parser.get_text()}


class ParserRegistry:
    """Registry mapping parser names to callables."""

    def __init__(self) -> None:
        self._parsers: Dict[str, Parser] = {}
        self.register("title", parse_title)
        self.register("links", parse_links)
        self.register("text", parse_text)

    def register(self, name: str, parser: Parser) -> None:
        self._parsers[name] = parser

    def unregister(self, name: str) -> None:
        self._parsers.pop(name, None)

    def get(self, name: str) -> Parser | None:
        return self._parsers.get(name)

    def available(self) -> List[str]:
        return sorted(self._parsers.keys())
