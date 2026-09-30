"""新华网食品频道 news.cn/food/ — 官方门户级食品资讯

覆盖：行业政策、头部企业新闻、食品安全、宏观产业趋势
权威背书，企业上市/重大公告的第一落点
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
    "绝味","盐津铺子","来伊份","零食很忙","赵一鸣","好想来","鸣鸣很忙",
    "休闲食品","食品工业","食品饮料","快消",
    "便利店","量贩","零食量贩","零食集合店",
    "门店","加盟","连锁","供应链","渠道","营销","品牌","消费","零售",
    "出口","上市","IPO","融资","并购","增长","营收","利润","产业",
    "安全","监管","标准","政策","国务院","工信部","农业农村部",
    "大健康","健康中国","消费升级","供给侧","内循环",,

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州"
]
class XinhuaFoodCrawler(BaseCrawler):
    name = "新华网食品"
    base_url = "https://www.news.cn"
    crawl_urls = [
        "https://www.news.cn/food/",
        "https://www.news.cn/food/index.htm",
        "https://www.news.cn/food/shipin_changjing.htm",
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
                            # news.cn 文章 URL 格式: /food/2026xxxx/xxxxxxxxx.htm
                            if not ("/food/" in href or "/food2/" in href): continue
                            # news.cn 有 2 种 URL:
                            # 1) /food/YYYYMMDD/32位hash/c.html (新式)
                            # 2) /food/YYYY-MM-DD/c_xxxxxx.htm (老式)
                            if not (re.search(r'/food/\d{8}/[a-f0-9]{32}/c\.html', href) or
                                    re.search(r'/food[0-9]*/\d{4}-\d{2}-\d{2}/c_\d+\.htm', href) or
                                    '/food/' in href and ('xinhuanet.com' in href or 'news.cn' in href)):
                                continue
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
            print(f"  [新华网食品] 失败: {str(e)[:60]}")
        return self._limit(items, 20)
