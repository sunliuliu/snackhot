"""RSSHub 爬虫 —— 自建 RSSHub 实例的零食相关路由

启动 RSSHub:
  docker compose -f docker-compose.rsshub.yml up -d
  访问: http://localhost:1200

零食相关 RSSHub 路由：
  - 知乎搜索:    /zhihu/search/{keyword}
  - 36氪搜索:     /36kr/search/{keyword}
  - B站搜索:      /bilibili/search/{keyword}
  - 虎嗅搜索:     /huxiu/search/{keyword}
  - 少数派搜索:   /sspai/search/{keyword}
  - 微信公众号:   /wechat/mp/homepage/{biz}  (需知 biz)
  - 微博用户:     /weibo/user/{uid}
"""
import asyncio, sys, os
from pathlib import Path
from typing import List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from .base import BaseCrawler
from models import RawItem
import httpx
from urllib.parse import quote
from datetime import datetime

# ============ 配置 ============
RSSHUB_BASE = os.environ.get("RSSHUB_BASE", "http://localhost:1200")

# 零食关键词 → RSSHub 路由映射
KEYWORDS = [
    "三只松鼠", "良品铺子", "卫龙", "盐津铺子", "洽洽食品", "来伊份",
    "好想来零食", "零食很忙", "赵一鸣零食", "零食行业", "量贩零食",
    "魔芋零食", "辣条", "坚果炒货", "糖果巧克力", "0糖食品",
]

# RSSHub 后端路由模板
ROUTE_TEMPLATES = [
    "/zhihu/search/{kw}",
    "/36kr/search/{kw}",
    "/bilibili/search/{kw}",
    "/huxiu/search/{kw}",
]


class RSSHubCrawler(BaseCrawler):
    """自建 RSSHub 爬虫（知乎/36氪/B站/虎嗅 搜索路由）"""

    name = "rsshub"
    description = f"RSSHub {len(ROUTE_TEMPLATES)} 后端 × {len(KEYWORDS)} 关键词"

    def __init__(self):
        super().__init__()
        self.base_url = RSSHUB_BASE

    async def fetch(self) -> List[RawItem]:
        """并发请求所有 RSSHub 路由"""
        import xml.etree.ElementTree as ET

        async def _fetch_one(url: str) -> List[RawItem]:
            try:
                async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        return []
                    # 解析 RSS
                    root = ET.fromstring(resp.content)
                    items = []
                    ns = {"atom": "http://www.w3.org/2005/Atom"}
                    for item in root.iter("item"):
                        title = (item.findtext("title") or "").strip()
                        link = (item.findtext("link") or "").strip()
                        desc = (item.findtext("description") or "").strip()
                        pub = item.findtext("pubDate") or item.findtext("published") or ""
                        if not title or not link:
                            continue
                        items.append(RawItem(
                            source_name="rsshub",
                            title=title[:80],
                            url=link,
                            raw_content=desc[:500] if desc else "",
                            published_at=self._parse_pub(pub),
                        ))
                    return items
            except Exception as e:
                return []

        urls = []
        for kw in KEYWORDS:
            for tpl in ROUTE_TEMPLATES:
                urls.append(f"{RSSHUB_BASE}{tpl.format(kw=quote(kw))}")

        print(f"  RSSHub: 请求 {len(urls)} 个路由...", flush=True)
        tasks = [_fetch_one(u) for u in urls]
        results = await asyncio.gather(*tasks)

        all_items = []
        for r in results:
            all_items.extend(r)

        # 去重
        seen = set()
        unique = []
        for it in all_items:
            if it.title not in seen:
                seen.add(it.title)
                unique.append(it)

        print(f"  RSSHub: {len(all_items)} → {len(unique)} 条有效", flush=True)
        return unique

    def _parse_pub(self, s: str) -> Optional[datetime]:
        if not s:
            return None
        fmts = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
        ]
        for fmt in fmts:
            try:
                return datetime.strptime(s.strip(), fmt)
            except:
                continue
        return None


if __name__ == "__main__":
    import requests  # noqa: F401  确保 import 链正确
    async def test():
        src = RSSHubCrawler()
        items = await src.fetch()
        for it in items[:5]:
            print(f"  [{it.source_name}] {it.title[:50]}")
    asyncio.run(test())