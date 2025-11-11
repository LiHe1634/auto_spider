"""FastAPI entrypoint exposing crawler management endpoints."""
from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db

app = FastAPI(title="Auto Spider", description="配置和管理爬虫的后台服务")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if _frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")

# 引用模型以便在应用启动时正确注册 ORM 元数据
_ = models.Crawler


@app.on_event("startup")
def on_startup() -> None:
    """Ensure the database schema is created on startup."""
    Base.metadata.create_all(bind=engine)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    if _frontend_dir.exists():
        return RedirectResponse(url="/frontend/")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Frontend not available")


@app.get("/api/crawlers", response_model=List[schemas.CrawlerRead])
def read_crawlers(db: Session = Depends(get_db)):
    """Return all crawlers."""
    return crud.list_crawlers(db)


@app.post("/api/crawlers", response_model=schemas.CrawlerRead, status_code=status.HTTP_201_CREATED)
def create_crawler(crawler_in: schemas.CrawlerCreate, db: Session = Depends(get_db)):
    """Create a new crawler."""
    return crud.create_crawler(db, crawler_in)


@app.get("/api/crawlers/{crawler_id}", response_model=schemas.CrawlerRead)
def read_crawler(crawler_id: int, db: Session = Depends(get_db)):
    return crud.get_crawler(db, crawler_id)


@app.put("/api/crawlers/{crawler_id}", response_model=schemas.CrawlerRead)
def update_crawler(crawler_id: int, crawler_in: schemas.CrawlerUpdate, db: Session = Depends(get_db)):
    return crud.update_crawler(db, crawler_id, crawler_in)


@app.delete("/api/crawlers/{crawler_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crawler(crawler_id: int, db: Session = Depends(get_db)):
    crud.delete_crawler(db, crawler_id)
    return None


@app.post("/api/crawlers/{crawler_id}/run", response_model=schemas.CrawlerRead)
def run_crawler(crawler_id: int, db: Session = Depends(get_db)):
    """Trigger a simulated crawler run."""
    return crud.run_crawler(db, crawler_id)
