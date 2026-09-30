"""36氪 - 食品餐饮板块 RSS（零食必在）"""
import httpx
from typing import List
from datetime import datetime
import feedparser
from .base import BaseCrawler
from models import RawItem

SNACK_KW = ["零食", "坚果", "辣条", "魔芋", "三只松鼠", "良品铺子", "百草味",
            "卫龙", "盐津铺子", "来伊份", "洽洽", "旺旺", "奥利奥",
            "饼干", "糖果", "巧克力", "肉脯", "果冻", "膨化", "烘焙",
            "糕点", "蜜饯", "炒货", "卤味", "休闲食品", "食品饮料", "餐饮",

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州"
]
class Kr36Crawler(BaseCrawler):
    name = "36氪-食品餐饮"
    crawl_urls = [
        # 36氪食品餐饮 RSS
        "https://36kr.com/feed",
        # 创业公司（零食品牌融资常在这）
        "https://36kr.com/feed/column/105",
    ]

    async def fetch(self) -> List[RawItem]:
        items = []
        for url in self.crawl_urls:
            try:
                async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        continue
                    feed = feedparser.parse(resp.text)
                    for entry in feed.entries:
                        title = entry.get("title", "")
                        link = entry.get("link", "")
                        summary = entry.get("summary", "")
                        combined = title + " " + summary
                        if any(kw in combined for kw in SNACK_KW):
                            pub = datetime.now()
                            if entry.get("published_parsed"):
                                try:
                                    pub = datetime(*entry.published_parsed[:6])
                                except Exception:
                                    pass
                            items.append(RawItem(
                                source_name=self.name,
                                title=title, url=link,
                                published_at=pub,
                                raw_content=summary[:500],
                            ))
            except Exception as e:
                print(f"[{self.name}] {url} 失败: {str(e)[:60]}")
                continue
        return self._limit(items, 30)