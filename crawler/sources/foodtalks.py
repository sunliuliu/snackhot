"""FoodTalks 全球食品资讯网 — FBIF 旗下权威食品媒体

覆盖：食品饮料全行业动态、创新、渠道、零售
每天 20-40 条，质量极高，是食品行业最垂直的媒体
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
    "休闲食品","食品饮料","食品工业","快消","快消品",
    "便利店","量贩","零食量贩","零食集合店",
    "门店","加盟","连锁","供应链","渠道","营销","品牌","消费","零售",
    "超市","大卖场","会员店","山姆","盒马","麦德龙","便利店",
    "茶饮","咖啡","乳制品","预制菜","调味料","方便食品",
    "出海","上市","IPO","融资","并购","增长","营收","利润",,

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州"
]
class FoodTalksCrawler(BaseCrawler):
    name = "FoodTalks"
    base_url = "https://www.foodtalks.cn"
    crawl_urls = [
        "https://www.foodtalks.cn/news",
        "https://www.foodtalks.cn/news/foodnews/general",
        "https://www.foodtalks.cn/news/tag/5570",  # 食品饮料 tag
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
                            if len(txt) < 12: continue
                            if not re.search(r'/news/\d+', href): continue
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
            print(f"  [FoodTalks] 失败: {str(e)[:60]}")
        return self._limit(items, 30)
