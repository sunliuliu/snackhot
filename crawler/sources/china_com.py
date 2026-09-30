"""中国网食品 food.china.com.cn — 国家级食品行业门户

真实 URL: http://food.china.com.cn/2026-09/18/content_118702205.shtml
"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx, re
from .base import BaseCrawler
from models import RawItem

KW = ["食品","饮料","零食","糖果","巧克力","三只松鼠","良品","卫龙","零食很忙",
      "休闲食品","食品工业","食品饮料","快消","便利店","量贩","零售","消费",
      "茶叶","咖啡","乳制品","预制菜","调味品","粮油","安全","监管","抽检",
      "召回","上市","融资","并购","增长","营收","利润","出口","产业园",
      "政策","国务院","工信部","农业农村部","创新","研发","技术","投资",

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州"
]
class ChinaComCrawler(BaseCrawler):
    name = "中国网食品"
    base_url = "https://food.china.com.cn"
    crawl_urls = [
        "https://food.china.com.cn/",
        "https://food.china.com.cn/shipin.htm",
    ]

    async def fetch(self) -> List[RawItem]:
        items: List[RawItem] = []
        seen = set()
        hdrs = dict(self.headers)
        hdrs.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://www.china.com.cn/",
        })
        try:
            async with httpx.AsyncClient(headers=hdrs, timeout=self.timeout,
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
                            # 真实格式: /2026-09/18/content_118702205.shtml
                            if not re.search(r'/[0-9]{4}-[0-9]{2}/[0-9]{2}/content_[0-9]+\.shtml', href): continue
                            if not any(kw in txt for kw in KW): continue
                            if href.startswith("//"): href = "https:" + href
                            elif href.startswith("/"): href = self.base_url + href
                            elif not href.startswith("http"): continue
                            key = href.split("?")[0]
                            if key in seen: continue
                            seen.add(key)
                            items.append(RawItem(source_name=self.name, title=txt, url=href, published_at=datetime.now()))
                    except Exception: continue
        except Exception as e: print(f"  [中国网食品] 失败: {str(e)[:60]}")
        return self._limit(items, 25)
