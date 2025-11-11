"""命令行工具。"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from .config import ConfigManager, CrawlerConfig
from .crawler import SpiderRunner
from .storage import ResultStorage


def _print_configs(configs: Iterable[CrawlerConfig]) -> None:
    for cfg in configs:
        print(f"- {cfg.name}")
        print(f"  URL: {cfg.start_url}")
        print(f"  Pattern: {cfg.pattern}")
        if cfg.description:
            print(f"  描述: {cfg.description}")
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="auto_spider 命令行工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_list = subparsers.add_parser("list", help="列出所有爬虫配置")

    parser_add = subparsers.add_parser("add", help="新增爬虫配置")
    parser_add.add_argument("name")
    parser_add.add_argument("start_url")
    parser_add.add_argument("pattern", help="用于匹配内容的正则表达式")
    parser_add.add_argument("-d", "--description", default="", help="配置描述")
    parser_add.add_argument("--overwrite", action="store_true", help="存在同名配置时覆盖")

    parser_remove = subparsers.add_parser("remove", help="删除爬虫配置")
    parser_remove.add_argument("name")

    parser_run = subparsers.add_parser("run", help="运行指定的爬虫")
    parser_run.add_argument("name")
    parser_run.add_argument("--no-save", action="store_true", help="不将结果写入文件")
    parser_run.add_argument("--export", type=Path, help="将结果导出到指定 JSON 文件")

    parser_results = subparsers.add_parser("results", help="查看历史结果列表")
    parser_results.add_argument("name")
    parser_results.add_argument("--show", action="store_true", help="展示最新一次结果内容")

    args = parser.parse_args(argv)

    manager = ConfigManager()
    storage = ResultStorage()
    runner = SpiderRunner()

    if args.command == "list":
        configs = manager.list_configs()
        if not configs:
            print("暂无配置，使用 add 命令添加新的爬虫。")
            return 0
        _print_configs(configs)
        return 0

    if args.command == "add":
        config = CrawlerConfig(
            name=args.name,
            start_url=args.start_url,
            pattern=args.pattern,
            description=args.description,
        )
        try:
            manager.add_config(config, overwrite=args.overwrite)
        except ValueError as exc:
            print(exc)
            return 1
        print(f"配置 {args.name} 已保存。")
        return 0

    if args.command == "remove":
        removed = manager.remove_config(args.name)
        if not removed:
            print(f"未找到名为 {args.name} 的配置。")
            return 1
        print(f"配置 {args.name} 已删除。")
        return 0

    if args.command == "run":
        config = manager.get_config(args.name)
        if not config:
            print(f"未找到名为 {args.name} 的配置。")
            return 1
        result = runner.run(config)
        print(result.summary())
        if not args.no_save:
            path = storage.save(result)
            print(f"结果已保存至 {path}")
        if args.export:
            ResultStorage.export([result], args.export)
            print(f"结果已导出到 {args.export}")
        return 0 if result.status == "success" else 1

    if args.command == "results":
        files = storage.list_results(args.name)
        if not files:
            print(f"未找到 {args.name} 的历史结果。")
            return 0
        for file in files:
            print(file)
        if args.show:
            latest = storage.load(files[-1])
            print("--- 最新结果 ---")
            print(latest)
        return 0

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
