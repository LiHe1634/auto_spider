# auto_spider

一个基于 Python 的小型爬虫系统，支持通过配置管理多个站点抓取任务。

## 功能概览

- 使用 JSON 文件维护爬虫配置，包含名称、目标地址与正则匹配规则。
- 提供命令行工具添加、删除、查看配置并运行爬虫。
- 基于正则表达式提取页面中的信息，并将抓取结果持久化到本地。
- 支持导出最新抓取结果，查看历史记录。

## 快速开始

1. 安装依赖（仅使用标准库，无需额外安装）。
2. 运行命令行工具：

```bash
python -m auto_spider.cli list
```

常用命令示例：

- 添加配置：

  ```bash
  python -m auto_spider.cli add news https://example.com/news "News (\\d+)" -d "示例新闻匹配"
  ```

- 查看配置：

  ```bash
  python -m auto_spider.cli list
  ```

- 运行爬虫并保存结果：

  ```bash
  python -m auto_spider.cli run news
  ```

- 查看历史结果：

  ```bash
  python -m auto_spider.cli results news --show
  ```

## 项目结构

- `auto_spider/config.py`：配置读写与管理。
- `auto_spider/crawler.py`：爬虫执行逻辑与结果对象。
- `auto_spider/storage.py`：抓取结果存储与导出。
- `auto_spider/cli.py`：命令行入口。
- `docs/plan.md`：按 README 要求制定的功能实现计划。
- `tests/`：单元测试。

## 开发与测试

执行以下命令运行测试：

```bash
pytest
```

测试使用 `pytest`，覆盖配置管理与爬虫执行的核心逻辑。
