"""Data access helpers for crawler management."""
from __future__ import annotations

from typing import Iterable, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


def list_crawlers(db: Session) -> Iterable[models.Crawler]:
    return db.execute(select(models.Crawler).order_by(models.Crawler.created_at.desc())).scalars().all()


def get_crawler(db: Session, crawler_id: int) -> models.Crawler:
    crawler = db.get(models.Crawler, crawler_id)
    if crawler is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawler not found")
    return crawler


def create_crawler(db: Session, crawler_in: schemas.CrawlerCreate) -> models.Crawler:
    crawler = models.Crawler(**crawler_in.dict())
    db.add(crawler)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Crawler with the same name already exists",
        ) from exc
    db.refresh(crawler)
    return crawler


def update_crawler(db: Session, crawler_id: int, crawler_in: schemas.CrawlerUpdate) -> models.Crawler:
    crawler = get_crawler(db, crawler_id)
    for key, value in crawler_in.dict(exclude_unset=True).items():
        setattr(crawler, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Crawler with the same name already exists",
        ) from exc
    db.refresh(crawler)
    return crawler


def delete_crawler(db: Session, crawler_id: int) -> None:
    crawler = get_crawler(db, crawler_id)
    db.delete(crawler)
    db.commit()


def run_crawler(db: Session, crawler_id: int, message: Optional[str] = None) -> models.Crawler:
    crawler = get_crawler(db, crawler_id)
    crawler.mark_run(status="success", message=message or "执行完成（模拟）")
    db.commit()
    db.refresh(crawler)
    return crawler
