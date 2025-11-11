# auto_spider

一个基于 FastAPI + SQLite 的小型爬虫配置系统，支持在后台创建、查看、维护爬虫任务并触发模拟执行。

## 功能特性

- 新建、编辑、删除爬虫配置（名称、目标站点、调度规则、启用状态及备注）。
- 查看爬虫列表及最近执行状态。
- 一键触发模拟执行，记录最后执行时间与状态。
- 自带简洁的前端页面，可直接通过浏览器管理配置。

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate  # Windows 请使用 .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 启动服务

```bash
uvicorn app.main:app --reload
```

服务默认监听在 <http://127.0.0.1:8000>，浏览器打开即可访问管理界面。

### 3. 运行测试

```bash
pytest
```

## 项目结构

```
app/
  crud.py          # 业务逻辑与数据库操作
  database.py      # 数据库连接与 Session 管理
  main.py          # FastAPI 入口，包含路由配置
  models.py        # SQLAlchemy ORM 模型
  schemas.py       # Pydantic 数据模型
frontend/
  index.html       # 前端单页应用
  app.js           # 调用后端接口的逻辑
  style.css        # 页面样式
```

默认数据库文件为 `data.db`，位于项目根目录，可通过环境变量 `DATABASE_URL` 指定其他存储位置或使用外部数据库。
