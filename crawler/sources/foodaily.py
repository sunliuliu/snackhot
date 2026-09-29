"""Foodaily 每日食品网 - 6 个零食分类页 + 快讯 + 资讯总览"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx
from .base import BaseCrawler
from models import RawItem

# 零食分类页（直接抓，无需关键词过滤）
FOODAILY_CATEGORIES = [
    ("7",  "零食"),
    ("13", "糖果巧克力"),
    ("9",  "饼干糕点"),
    ("11", "肉脯卤味"),
    ("10", "坚果炒货"),
    ("8",  "膨化食品"),
]
# 快讯（每日早报里会汇总行业动态）
FOODAILY_FEEDS = [
    "https://www.foodaily.com/index.php/newsflashes",
    "https://www.foodaily.com/index.php/articles",
]

class FoodailyCrawler(BaseCrawler):
    name = "Foodaily 每日食品"
    base_url = "https://www.foodaily.com"

    async def fetch(self) -> List[RawItem]:
        items: List[RawItem] = []
        seen = set()
        headers = {**self.headers}

        # A. 分类页（最稳定，无关键词误判）
        for cid, cname in FOODAILY_CATEGORIES:
            url = f"{self.base_url}/index.php/articles?catId={cid}"
            items.extend(await self._fetch_page(url, f"Foodaily-{cname}", items, seen))

        # B. 快讯 + 总览（补漏）
        for url in FOODAILY_FEEDS:
            items.extend(await self._fetch_page(url, self.name, items, seen))

        return self._limit(items, 60)

    async def _fetch_page(self, url: str, source_label: str, all_items: list, seen: set) -> List[RawItem]:
        items = []
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    return []
                soup = BeautifulSoup(resp.text, "lxml")
                for a in soup.find_all("a", href=True):
                    href = a.get("href", "")
                    title = a.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    if "/articles/" not in href and "/newsflashes/" not in href:
                        continue
                    if href.startswith("//"):
                        href = "https:" + href
                    elif href.startswith("/"):
                        href = self.base_url + href
                    elif not href.startswith("http"):
                        continue
                    # 去重
                    key = href.split("?")[0]
                    if key in seen or any(href in i.url for i in all_items):
                        continue
                    seen.add(key)
                    items.append(RawItem(
                        source_name=source_label,
                        title=title, url=href,
                        published_at=datetime.now(),
                    ))
        except Exception as e:
            print(f"  [{source_label}] {url.split('?')[-1] or '总览'} 失败: {str(e)[:50]}")
        return items