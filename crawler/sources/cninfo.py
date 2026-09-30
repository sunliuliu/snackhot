"""巨潮资讯 - 零食/食品相关上市公司公告（搜索接口版）

策略: 优先用 fulltextSearch 搜索接口 (按公司名搜索, 更精准)
      fallback: hisAnnouncement 全量拉取 + 本地关键词过滤

30 家 A 股 + 港股食品/零食上市公司
"""
import asyncio, json, re, urllib.parse
from typing import List
from datetime import datetime, timedelta
import httpx
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sources.base import BaseCrawler
from models import RawItem

# ============ 30 家上市公司 ============
SNACK_STOCKS = {
    "300783": "三只松鼠", "603716": "良品铺子", "002847": "盐津铺子",
    "603887": "来伊份", "603517": "绝味食品", "002557": "洽洽食品",
    "002695": "煌上煌", "01458": "周黑鸭", "09985": "卫龙",
    "603866": "桃李面包", "603886": "元祖股份", "002820": "桂发祥",
    "605499": "东鹏饮料", "603156": "养元饮品", "603711": "香飘飘",
    "600887": "伊利股份", "603288": "海天味业", "600298": "安琪酵母",
    "600872": "中炬高新", "002702": "海欣食品", "002582": "好想你",
    "000716": "黑芝麻", "002495": "佳隆股份", "002661": "克明面业",
    "600305": "恒顺醋业", "603345": "安井食品", "002216": "三全食品",
    "002699": "美盛文化", "300999": "金龙鱼",
}

class CninfoCrawler(BaseCrawler):
    name = "巨潮资讯"
    base_url = "http://www.cninfo.com.cn"

    async def fetch(self) -> List[RawItem]:
        items = []
        seen_urls = set()
        today = datetime.now()
        start_date = (today - timedelta(days=10)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        headers = {**self.headers, "Origin": self.base_url, "Referer": self.base_url + "/"}

        async with httpx.AsyncClient(headers=headers, timeout=self.timeout, follow_redirects=True) as client:
            # 策略 1: 按公司名搜索 (精准)
            for code, name in SNACK_STOCKS.items():
                try:
                    enc = urllib.parse.quote(name)
                    url = f"{self.base_url}/new/fulltextSearch/full?searchkey={enc}&sdate={start_date}&edate={end_date}&isfulltext=false&sortName=pubdate&sortType=desc&pageNum=1&pageSize=10"
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        await asyncio.sleep(0.3)
                        continue
                    try:
                        data = resp.json()
                    except Exception:
                        continue
                    for ann in (data.get("announcements") or []):
                        title = (ann.get("announcementTitle", "") or "").replace("<em>", "").replace("</em>", "")
                        sec_name = ann.get("secName", "") or name
                        ann_id = ann.get("announcementId", "")
                        c = ann.get("secCode", code)
                        if not title or not ann_id: continue
                        full_url = f"{self.base_url}/new/disclosure/detail?stockCode={c}&announcementId={ann_id}"
                        if full_url in seen_urls: continue
                        seen_urls.add(full_url)
                        items.append(RawItem(
                            source_name=f"巨潮-{sec_name}", title=title, url=full_url,
                            published_at=datetime.now(),
                            raw_content=f"{sec_name}({c}) {title[:40]}",
                        ))
                    await asyncio.sleep(0.3)
                except Exception:
                    continue

            # 策略 2: 全量拉取 + 零食关键词过滤 (fallback, 少于 3 条时触发)
            if len(items) < 3:
                SNACK_KW = ["零食", "坚果", "辣条", "魔芋", "休闲食品", "预制菜", "卤味", "糖果", "巧克力",

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州"
]
                for column in ["szse", "sse"]:
                    try:
                        payload = {
                            "pageSize": 50, "pageNum": 1,
                            "seDate": f"{start_date}~{end_date}",
                            "tabName": "fulltext", "column": column,
                            "category": "", "plate": "",
                        }
                        resp = await client.post(f"{self.base_url}/new/hisAnnouncement/query", data=payload)
                        if resp.status_code != 200: continue
                        data = resp.json()
                        for ann in (data.get("announcements") or []):
                            title = (ann.get("announcementTitle", "") or "").replace("<em>", "").replace("</em>", "")
                            sec_name = ann.get("secName", "")
                            if not title: continue
                            has_kw = any(kw in title for kw in SNACK_KW)
                            is_stock = any(n in sec_name for n in SNACK_STOCKS.values())
                            if has_kw or is_stock:
                                c = ann.get("secCode", "")
                                ann_id = ann.get("announcementId", "")
                                full_url = f"{self.base_url}/new/disclosure/detail?stockCode={c}&announcementId={ann_id}"
                                if full_url not in seen_urls:
                                    seen_urls.add(full_url)
                                    items.append(RawItem(
                                        source_name=f"巨潮-{sec_name or c}", title=title, url=full_url,
                                        published_at=datetime.now(), raw_content=f"{sec_name}({c})",
                                    ))
                        await asyncio.sleep(1.0)
                    except Exception:
                        continue

        print(f"  [cninfo] {len(items)} 条 (30 家上市公司, 搜索接口优先)")
        return self._limit(items, 50)
