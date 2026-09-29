"""新浪财经 - 食品饮料新闻（宽泛预过滤）"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx, re
from .base import BaseCrawler
from models import RawItem
from .eastmoney import WIDE_FOOD_KW  # 复用东财的关键词列表

class SinaFinanceCrawler(BaseCrawler):
    name = "新浪财经"
    crawl_urls = ["https://finance.sina.com.cn/roll/"]

    async def fetch(self) -> List[RawItem]:
        items: List[RawItem] = []
        seen = set()
        for url in self.crawl_urls:
            try:
                async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        continue
                    soup = BeautifulSoup(resp.text, "lxml")
                    for a in soup.find_all("a", href=True):
                        href = a.get("href", "")
                        title = a.get_text(strip=True)
                        if not title or len(title) < 15: continue
                        if not ("sina.com.cn" in href and ".shtml" in href): continue
                        if "video" in href or "slide" in href: continue
                        if not any(kw in title for kw in WIDE_FOOD_KW): continue
                        key = href.split("?")[0]
                        if key in seen: continue
                        seen.add(key)
                        items.append(RawItem(
                            source_name=self.name, title=title, url=href,
                            published_at=datetime.now(),
                        ))
            except Exception as e:
                print(f"  [新浪] 失败: {str(e)[:50]}")
        return self._limit(items, 20)