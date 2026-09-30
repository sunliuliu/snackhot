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
      "技术","研究","进展","机制","活性","品质","风味","营养",

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州",
    # 扩充品牌词库
    "鸣鸣很忙", "零食很忙", "赵一鸣", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "旺旺", "卫龙", "盐津铺子", "绝味", "洽洽", "亿滋", "玛氏", "雀巢", "好时", "百事", "可口可乐", "农夫山泉", "元气森林", "伊利", "蒙牛", "光明", "娃哈哈", "康师傅", "统一", "双汇", "安井", "三全", "思念", "劲仔", "麻辣王子", "甘源", "喜茶", "奈雪的茶", "茶颜悦色", "霸王茶姬", "蜜雪冰城", "古茗", "一点点", "CoCo", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "奥利奥", "大白兔", "徐福记", "达利园", "盼盼", "好丽友", "金丝猴", "马大姐"
]
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
