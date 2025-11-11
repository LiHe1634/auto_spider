# auto_spider

一个基于 Python 的轻量级爬虫配置与运行系统。它提供了下列特性：

- 使用 JSON 文件存储爬虫配置，支持新增、更新、删除和批量导入。
- 通过 `SpiderManager` 统一管理爬虫，并可在代码或命令行中运行。
- 内置标题、链接、纯文本三种解析器，可自行扩展。
- 采用标准库实现 HTTP 抓取，无需额外依赖。

## 快速开始

```bash
# 运行测试
pytest

# 使用命令行列出当前配置的爬虫
python -m auto_spider --config spiders.json list
```

### 配置示例

配置文件 `spiders.json` 为一个 JSON 数组，其中每个对象对应一个爬虫：

```json
[
  {
    "name": "example",
    "start_url": "https://example.com",
    "parser": "title",
    "enabled": true,
    "extra": {}
  }
]
```

## 运行爬虫

在代码中可以这样使用：

```python
from auto_spider import SpiderConfig, SpiderManager

manager = SpiderManager(config_path="spiders.json")
manager.add_spider(SpiderConfig(name="example", start_url="https://example.com", parser="title"))
result = manager.run_spider("example")
print(result.data)
```

命令行运行：

```bash
python -m auto_spider --config spiders.json run example
```

命令行同样支持新增和删除爬虫配置：

```bash
python -m auto_spider --config spiders.json add example https://example.com title
python -m auto_spider --config spiders.json remove example
```
