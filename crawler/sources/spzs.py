"""食品招商网 spzs.com — 食品B2B招商/资讯平台"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx, re
from .base import BaseCrawler
from models import RawItem

KW = ["食品","饮料","零食","糖果","巧克力","三只松鼠","良品","卫龙","零食很忙",
      "休闲食品","食品饮料","快消","品牌","渠道","招商","代理","加盟",
      "茶叶","咖啡","乳制品","预制菜","调味品","粮油","特产","进口"]

class SpzsCrawler(BaseCrawler):
    name = "食品招商网"
    base_url = "https://www.spzs.com"
    crawl_urls = [
        "https://www.spzs.com/news/",
        "https://www.spzs.com/shipin/",
        "https://www.spzs.com/yinliao/",
        "https://www.spzs.com/lingshi/",
    ]

    async def fetch(self) -> List[RawItem]:
        items: List[RawItem] = []
        seen = set()
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                for url in self.crawl_urls:
                    try:
                        resp = await client.get(url)
                        if resp.status_code != 200: continue
                        soup = BeautifulSoup(resp.text, "lxml")
                        for a in soup.find_all("a", href=True):
                            txt = a.get_text(strip=True)
                            href = a.get("href", "")
                            if len(txt) < 10: continue
                            if not ("/news/" in href or "/shipin/" in href or "/yinliao/" in href or "/lingshi/" in href): continue
                            if not re.search(r'[0-9]{4,}', href): continue
                            if not any(kw in txt for kw in KW): continue
                            if href.startswith("//"): href = "https:" + href
                            elif href.startswith("/"): href = self.base_url + href
                            elif not href.startswith("http"): continue
                            key = href.split("?")[0]
                            if key in seen: continue
                            seen.add(key)
                            items.append(RawItem(source_name=self.name, title=txt, url=href, published_at=datetime.now()))
                    except Exception: continue
        except Exception as e: print(f"  [食品招商网] 失败: {str(e)[:60]}")
        return self._limit(items, 25)
