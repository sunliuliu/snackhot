"""中国证券报 cnstock.com — 资本市场食品板块"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx, re
from .base import BaseCrawler
from models import RawItem

KW = ["食品","饮料","零食","糖果","巧克力","三只松鼠","良品","卫龙","盐津铺子",
      "绝味","洽洽","旺旺","来伊份","海天","伊利","蒙牛","茅台","五粮液",
      "休闲食品","食品饮料","快消","上市公司","IPO","融资","并购","重组",
      "增长","营收","利润","财报","业绩预告","解禁","回购","增持"]

class CnstockCrawler(BaseCrawler):
    name = "中国证券报"
    base_url = "https://www.cnstock.com"
    crawl_urls = [
        "https://www.cnstock.com/ssgs/",
        "https://www.cnstock.com/cjxw/index.html",
        "https://search.cnstock.com/?searchword=食品饮料",
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
                            if not (re.search(r'/ssgs/[0-9]{8,}/[0-9]+\.htm', href) or
                                    re.search(r'/cjxw/[0-9]{8,}/[0-9]+\.htm', href) or
                                    re.search(r'/news/[0-9]+\.htm', href)): continue
                            if not any(kw in txt for kw in KW): continue
                            if href.startswith("//"): href = "https:" + href
                            elif href.startswith("/"): href = self.base_url + href
                            elif not href.startswith("http"): continue
                            key = href.split("?")[0]
                            if key in seen: continue
                            seen.add(key)
                            items.append(RawItem(source_name=self.name, title=txt, url=href, published_at=datetime.now()))
                    except Exception: continue
        except Exception as e: print(f"  [中国证券报] 失败: {str(e)[:60]}")
        return self._limit(items, 25)
