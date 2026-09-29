"""统一数据模型"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class RawItem(BaseModel):
    source_name: str
    title: str
    url: str
    published_at: Optional[datetime] = None
    raw_content: str = ""
    author: Optional[str] = None


class ProcessedItem(BaseModel):
    id: str
    source_name: str
    title: str
    original_title: Optional[str] = None
    url: str
    published_at: Optional[datetime] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    summary: str = ""
    category: str = "other"
    brand_tags: List[str] = Field(default_factory=list)
    event_type: str = "other"
    score: int = 0
    selected: bool = False
    reason: str = ""
    story_id: Optional[str] = None


class EventCluster(BaseModel):
    id: str
    title: str
    summary: str
    category: str
    brand_tags: List[str] = Field(default_factory=list)
    event_type: str
    member_ids: List[str] = Field(default_factory=list)
    source_count: int = 0
    signal_count: int = 0
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    hot_score: float = 0.0
    rank: Optional[int] = None


class DailyReport(BaseModel):
    date: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    highlights: List[str] = Field(default_factory=list)
    sections: List[dict] = Field(default_factory=list)
    source_count: int = 0
    item_count: int = 0
