"""中国供销合作网 chinacoop.gov.cn — 供销社系统食品/农产品流通

GBK 编码, 旧式 .shtml URL
"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx, re
from .base import BaseCrawler
from models import RawItem

KW = ["食品","饮料","零食","农产品","茶叶","粮油","果蔬","生鲜",
      "流通","销售","合作社","供销社","农超对接","冷链","配送",
      "批发","市场","政策","改革","合作","签约","项目",

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州"
]
class ChinacoopCrawler(BaseCrawler):
    name = "中国供销合作网"
    base_url = "http://www.chinacoop.gov.cn"
    crawl_urls = [
        "http://www.chinacoop.gov.cn/",
        "http://www.chinacoop.gov.cn/xwdt/",
        "http://www.chinacoop.gov.cn/xwdt/index.htm",
    ]

    async def fetch(self) -> List[RawItem]:
        items: List[RawItem] = []
        seen = set()
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout,
                                         follow_redirects=True, verify=False) as client:
                for url in self.crawl_urls:
                    try:
                        resp = await client.get(url)
                        if resp.status_code != 200: continue
                        # GBK fallback
                        html = resp.text
                        try:
                            d = resp.content.decode("gbk", errors="ignore")
                            if any("\u4e00" <= c <= "\u9fff" for c in d[:1000]):
                                html = d
                        except: pass
                        soup = BeautifulSoup(html, "lxml")
                        for a in soup.find_all("a", href=True):
                            txt = a.get_text(strip=True)
                            href = a.get("href", "")
                            if len(txt) < 12: continue
                            if not ("/xwdt/" in href or "/dtxx/" in href or "/gsgg/" in href or
                                    href.endswith(".shtml") or href.endswith(".htm")): continue
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
        except Exception as e: print(f"  [中国供销合作网] 失败: {str(e)[:60]}")
        return self._limit(items, 20)
