"""cnfood.cn 中国食品报 — 行业第一大报的数字版

覆盖：食品产业全链条、宏观政策、食品安全、企业经营
最老牌的食品行业官方媒体之一
"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx, re
from .base import BaseCrawler
from models import RawItem

WIDE_KW = [
    "食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙",
    "辣条","魔芋","奥利奥","饼干","烘焙","肉脯","卤味","洽洽","旺旺",
    "绝味","盐津铺子","来伊份","零食很忙","赵一鸣","好想来",
    "休闲食品","食品工业","食品饮料","快消",
    "便利店","量贩","零食量贩","零食集合店",
    "门店","加盟","连锁","供应链","渠道","营销","品牌","消费","零售",
    "茶","咖啡","乳制品","预制菜","调味品","方便食品","粮油",
    "出口","上市","IPO","融资","并购","增长","营收","利润",
    "安全","监管","标准","抽检","召回","国标","食品添加剂","市场监管",
    "产业园","加工","制造","工厂","生产","技术","创新","研发",
]

class CnfoodCrawler(BaseCrawler):
    name = "中国食品报"
    base_url = "https://www.cnfood.cn"
    crawl_urls = [
        "https://www.cnfood.cn",
        "https://www.cnfood.cn/news/",
        "https://www.cnfood.cn/channel/index_1.html",  # 行业要闻
        "https://www.cnfood.cn/channel/index_5.html",  # 食安监管
    ]

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
                            if len(txt) < 10: continue
                            if not re.search(r'(/news/\d+|/detail_\d+|/article/\d+)', href): continue
                            if not any(kw in txt for kw in WIDE_KW): continue
                            if href.startswith("//"): href = "https:" + href
                            elif href.startswith("/"): href = self.base_url + href
                            elif not href.startswith("http"): continue
                            key = href.split("?")[0]
                            if key in seen: continue
                            seen.add(key)
                            items.append(RawItem(
                                source_name=self.name, title=txt, url=href,
                                published_at=datetime.now(),
                            ))
                    except Exception:
                        continue
        except Exception as e:
            print(f"  [中国食品报] 失败: {str(e)[:60]}")
        return self._limit(items, 25)
