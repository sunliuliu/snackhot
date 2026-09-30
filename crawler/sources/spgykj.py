"""食品工业科技 spgykj.com — 核心期刊 + 行业动态

真实 URL: /article/doi/10.13386/j.issn1002-0306.YYYYNNNN
"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx, re
from .base import BaseCrawler
from models import RawItem

KW = ["食品","饮料","零食","微生物","发酵","保鲜","工艺","配方",
      "检测","安全","添加剂","防腐剂","抗氧化","酶","蛋白质",
      "技术","研究","进展","机制","活性","品质","风味","营养"]

class SpgykjCrawler(BaseCrawler):
    name = "食品工业科技"
    base_url = "https://www.spgykj.com"
    crawl_urls = ["https://www.spgykj.com/"]

    async def fetch(self) -> List[RawItem]:
        items: List[RawItem] = []
        seen = set()
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout,
                                         follow_redirects=True) as client:
                for url in self.crawl_urls:
                    try:
                        resp = await client.get(url)
                        if resp.status_code != 200: continue
                        soup = BeautifulSoup(resp.text, "lxml")
                        for a in soup.find_all("a", href=True):
                            txt = a.get_text(strip=True)
                            href = a.get("href", "")
                            if len(txt) < 15: continue
                            if not ("/article/doi/" in href or "/article/" in href): continue
                            if not any(kw in txt for kw in KW): continue
                            if href.startswith("//"): href = "https:" + href
                            elif href.startswith("/"): href = self.base_url + href
                            elif not href.startswith("http"): continue
                            key = href.split("?")[0]
                            if key in seen: continue
                            seen.add(key)
                            items.append(RawItem(source_name=self.name, title=txt, url=href, published_at=datetime.now()))
                    except Exception: continue
        except Exception as e: print(f"  [食品工业科技] 失败: {str(e)[:60]}")
        return self._limit(items, 25)
