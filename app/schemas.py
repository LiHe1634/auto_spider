"""Pydantic schemas for request and response bodies."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class CrawlerBase(BaseModel):
    name: str = Field(..., max_length=100, description="用于标识爬虫的名称")
    target_url: HttpUrl = Field(..., description="爬虫目标站点地址")
    schedule: Optional[str] = Field(None, max_length=100, description="调度表达式或描述")
    enabled: bool = Field(True, description="是否启用该爬虫")
    notes: Optional[str] = Field(None, description="备注信息")


class CrawlerCreate(CrawlerBase):
    """Schema used when creating a crawler."""


class CrawlerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    target_url: Optional[HttpUrl] = None
    schedule: Optional[str] = Field(None, max_length=100)
    enabled: Optional[bool] = None
    notes: Optional[str] = None


class CrawlerRead(CrawlerBase):
    id: int
    last_run_at: Optional[datetime] = None
    last_run_status: str
    last_run_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
