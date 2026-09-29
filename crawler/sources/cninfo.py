"""巨潮资讯 - 零食相关上市公司公告"""
from typing import List
from datetime import datetime, timedelta
import httpx
from .base import BaseCrawler
from models import RawItem

# 零食行业相关 A 股 + 港股
SNACK_STOCKS = {
    "300783": "三只松鼠",
    "603887": "来伊份",
    "002847": "盐津铺子",
    "603517": "绝味食品",
    "603716": "良品铺子",
    "002557": "洽洽食品",
    "600872": "中炬高新",
    "002699": "美盛文化",
    "600305": "恒顺醋业",
}
# 零食关键词过滤（上市公司可能带零食字样的公告）
SNACK_KEYWORDS = ["零食", "坚果", "辣条", "魔芋", "三只松鼠", "良品铺子", "百草味",
                  "卫龙", "盐津铺子", "来伊份", "洽洽", "旺旺", "奥利奥",
                  "饼干", "糖果", "巧克力", "肉脯", "果冻", "膨化",
                  "烘焙", "糕点", "蜜饯", "炒货", "卤味", "休闲食品"]

class CninfoCrawler(BaseCrawler):
    name = "巨潮资讯"
    base_url = "http://www.cninfo.com.cn"

    async def fetch(self) -> List[RawItem]:
        items = []
        today = datetime.now()
        start_date = (today - timedelta(days=3)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        try:
            # 拉全量 A 股公告（巨潮按 secid 过滤不稳定，先拉全量再本地过滤）
            payload = {
                "pageSize": 50, "pageNum": 1,
                "seDate": f"{start_date}~{end_date}",
                "tabName": "fulltext", "column": "szse",
                "category": "", "plate": "",
            }
            headers = {**self.headers, "Origin": self.base_url, "Referer": self.base_url + "/"}
            async with httpx.AsyncClient(headers=headers, timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.post(f"{self.base_url}/new/hisAnnouncement/query", data=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    anns = data.get("announcements") or []
                    for ann in anns:
                        sec_name = ann.get("secName", "") or ann.get("secNameCn", "")
                        title = ann.get("announcementTitle", "").replace("<em>", "").replace("</em>", "")
                        # 过滤：要么是零食上市公司，要么公告里有零食关键词
                        is_snack_stock = any(name in sec_name for name in SNACK_STOCKS.values())
                        has_kw = any(kw in title or kw in ann.get("adjunctUrl","") for kw in SNACK_KEYWORDS)
                        if title and (is_snack_stock or has_kw):
                            code = ann.get("secCode", "")
                            ann_id = ann.get("announcementId", "")
                            url = f"{self.base_url}/new/disclosure/detail?stockCode={code}&announcementId={ann_id}"
                            items.append(RawItem(
                                source_name=f"巨潮资讯-{sec_name or code}",
                                title=title,
                                url=url,
                                published_at=datetime.now(),
                                raw_content=f"股票 {code} {sec_name} 的公告",
                            ))
        except Exception as e:
            print(f"[{self.name}] 抓取失败: {e}")

        # 额外：精准抓零食上市公司（直接带 secid 试试）
        for code, name in SNACK_STOCKS.items():
            try:
                payload2 = {
                    "pageSize": 10, "pageNum": 1,
                    "seDate": f"{start_date}~{end_date}",
                    "tabName": "fulltext", "column": "szse",
                    "category": "",
                    "stock": f"{name},{code}",
                }
                async with httpx.AsyncClient(headers=headers, timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.post(f"{self.base_url}/new/hisAnnouncement/query", data=payload2)
                    if resp.status_code == 200:
                        data = resp.json()
                        anns2 = data.get("announcements") or []
                        for ann in anns2:
                            title = ann.get("announcementTitle","").replace("<em>","").replace("</em>","")
                            if title:
                                ann_id = ann.get("announcementId","")
                                url = f"{self.base_url}/new/disclosure/detail?stockCode={code}&announcementId={ann_id}"
                                # 去重
                                if not any(i.url == url for i in items):
                                    items.append(RawItem(
                                        source_name=f"巨潮资讯-{name}",
                                        title=title, url=url,
                                        published_at=datetime.now(),
                                        raw_content=f"{name}({code}) 的公告",
                                    ))
            except Exception as e:
                print(f"  [{self.name}] {name}({code}) 失败: {str(e)[:60]}")
                continue

        return self._limit(items, 40)