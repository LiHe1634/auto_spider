"""Command line interface for the project."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Any, Dict

from .manager import SpiderManager
from .models import SpiderConfig


def _parse_extra(pairs: list[str]) -> Dict[str, Any]:
    extra: Dict[str, Any] = {}
    for item in pairs:
        if "=" not in item:
            raise argparse.ArgumentTypeError("extra parameters must be in key=value format")
        key, value = item.split("=", 1)
        extra[key] = value
    return extra


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage auto_spider spiders")
    parser.add_argument("--config", dest="config", default="spiders.json", help="Configuration file path")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List configured spiders")

    add_parser = sub.add_parser("add", help="Add a new spider")
    add_parser.add_argument("name")
    add_parser.add_argument("url")
    add_parser.add_argument("parser")
    add_parser.add_argument("--disabled", action="store_true", help="Create the spider in a disabled state")
    add_parser.add_argument("--extra", nargs="*", default=[], help="Additional key=value pairs", metavar="KEY=VALUE")

    remove_parser = sub.add_parser("remove", help="Remove an existing spider")
    remove_parser.add_argument("name")

    run_parser = sub.add_parser("run", help="Run a configured spider")
    run_parser.add_argument("name")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    manager = SpiderManager(config_path=args.config)

    if args.command == "list":
        for config in manager.list_spiders():
            print(json.dumps(config.to_dict(), ensure_ascii=False))
        return 0

    if args.command == "add":
        config = SpiderConfig(
            name=args.name,
            start_url=args.url,
            parser=args.parser,
            enabled=not args.disabled,
            extra=_parse_extra(args.extra),
        )
        manager.add_spider(config)
        print(f"Added spider '{config.name}'")
        return 0

    if args.command == "remove":
        manager.remove_spider(args.name)
        print(f"Removed spider '{args.name}'")
        return 0

    if args.command == "run":
        result = manager.run_spider(args.name)
        print(json.dumps(asdict(result), default=str, ensure_ascii=False, indent=2))
        return 0

    raise RuntimeError("Unknown command")  # pragma: no cover - argparse ensures coverage


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
