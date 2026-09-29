"""抓取器基类"""
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, timedelta
import httpx
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import RawItem
from config import REQUEST_HEADERS, REQUEST_TIMEOUT, MAX_ITEMS_PER_SOURCE


class BaseCrawler(ABC):
    name: str = "base"
    base_url: str = ""
    crawl_urls: List[str] = []

    def __init__(self):
        self.headers = REQUEST_HEADERS
        self.timeout = REQUEST_TIMEOUT

    @abstractmethod
    async def fetch(self) -> List[RawItem]:
        """子类实现具体抓取逻辑"""
        ...

    async def _get(self, url: str) -> str:
        # 速率控制：每个请求前 await，自动按节奏等够
        try:
            from services.rate_limiter import RateLimiter
            await RateLimiter().wait(self.name)
        except Exception:
            pass
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text

    def _is_recent(self, dt: datetime, hours: int = 48) -> bool:
        if dt is None:
            return True  # 抓不到时间的先保留
        now = datetime.now()
        # naive vs aware 处理
        if dt.tzinfo and now.tzinfo is None:
            now = now.replace(tzinfo=dt.tzinfo)
        return (now - dt).total_seconds() < hours * 3600

    def _limit(self, items: List[RawItem], n: int = MAX_ITEMS_PER_SOURCE) -> List[RawItem]:
        return items[:n]
