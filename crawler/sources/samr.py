"""国家市场监管总局 samr.gov.cn — 食品抽检/监管通报"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx, re
from .base import BaseCrawler
from models import RawItem

KW = ["食品","饮料","零食","糖果","巧克力","坚果","乳制品","饮料","茶叶","酒",
      "安全","抽检","召回","不合格","通报","处置","整改","专项整治","监督",
    # ===== 品牌扩充 (2026-09-30) =====
    "鸣鸣很忙","零食很忙","赵一鸣","好想来","老婆大人","来优品","万辰集团",
    "良品铺子","三只松鼠","来伊份","薛记炒货","卫龙","盐津铺子","绝味","洽洽",
    "旺旺","怡口莲","亿滋","玛氏","雀巢","好时","百事","可口可乐","农夫山泉",
    "元气森林","伊利","蒙牛","光明","娃哈哈","康师傅","统一","双汇","安井","三全","思念",
    "劲仔","麻辣王子","甘源","喜茶","奈雪的茶","茶颜悦色","霸王茶姬","蜜雪冰城",
    "零食有鸣","糖巢","零食优选","爱零食","戴永红",
    "零食舱","桔子花开","零食顽家","金粒门","几多全","一栗",
    "奥利奥","大白兔","徐福记","达利园","盼盼","好丽友","金丝猴","马大姐",
      "市监","市场监管","食品添加剂","防腐剂","超标","假冒","伪劣","投诉","举报"]

class SamrCrawler(BaseCrawler):
    name = "市监总局"
    base_url = "https://www.samr.gov.cn"
    crawl_urls = [
        "https://www.samr.gov.cn/spcjs/",
        "https://www.samr.gov.cn/spcjs/sjcb/",
        "https://www.samr.gov.cn/sp/",
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
                            if len(txt) < 12: continue
                            if not ("/spcjs/" in href or "/sp/" in href): continue
                            if not any(kw in txt for kw in KW): continue
                            if href.startswith("//"): href = "https:" + href
                            elif href.startswith("/"): href = self.base_url + href
                            elif not href.startswith("http"): continue
                            key = href.split("?")[0]
                            if key in seen: continue
                            seen.add(key)
                            items.append(RawItem(source_name=self.name, title=txt, url=href, published_at=datetime.now()))
                    except Exception: continue
        except Exception as e: print(f"  [市监总局] 失败: {str(e)[:60]}")
        return self._limit(items, 20)
