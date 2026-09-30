"""巨潮资讯 - 零食/食品相关上市公司公告（扩展版）

零食行业 A 股 + 港股完整列表（30+ 家）:
  零食/卤味/坚果: 三只松鼠、良品铺子、盐津铺子、来伊份、绝味食品、洽洽食品、
                煌上煌、周黑鸭、卫龙(港)
  烘焙/糕点:     桃李面包、元祖股份、桂发祥
  糖果巧克力:    金种子酒(白酒)、(巧克力企业多未上市)
  饮料/乳品:     东鹏饮料、养元饮品、香飘飘、伊利股份、海天味业
  综合食品:       中炬高新、海欣食品、好想你、黑芝麻、佳隆股份、安琪酵母、克明面业
  冷冻/预制菜:    安井食品、三全食品
  其他:          恒顺醋业、美盛文化
"""
from typing import List
from datetime import datetime, timedelta
import httpx
from .base import BaseCrawler
from models import RawItem

# ============ 扩展后的上市公司列表 (A 股 + 港股) ============
SNACK_STOCKS = {
    # --- 零食/卤味/坚果 (核心) ---
    "300783": "三只松鼠",
    "603716": "良品铺子",
    "002847": "盐津铺子",
    "603887": "来伊份",
    "603517": "绝味食品",
    "002557": "洽洽食品",
    "002695": "煌上煌",
    "01458":  "周黑鸭",     # 港股
    "09985":  "卫龙",       # 港股

    # --- 烘焙/糕点 ---
    "603866": "桃李面包",
    "603886": "元祖股份",
    "002820": "桂发祥",

    # --- 饮料/乳品/调味 ---
    "605499": "东鹏饮料",
    "603156": "养元饮品",
    "603711": "香飘飘",
    "600887": "伊利股份",
    "603288": "海天味业",
    "600298": "安琪酵母",
    "600519": "贵州茅台",    # 虽非零食但食品行业巨头，公告有时涉及食品趋势

    # --- 综合食品 ---
    "600872": "中炬高新",
    "002702": "海欣食品",
    "002582": "好想你",
    "000716": "黑芝麻",
    "002495": "佳隆股份",
    "002661": "克明面业",
    "600305": "恒顺醋业",

    # --- 冷冻/预制菜 ---
    "603345": "安井食品",
    "002216": "三全食品",

    # --- 其他食品相关 ---
    "002699": "美盛文化",
    "300999": "金龙鱼",      # 粮油巨头
}

# 零食关键词（扩展版）
SNACK_KEYWORDS = [
    "零食", "坚果", "辣条", "魔芋", "三只松鼠", "良品铺子", "百草味",
    "卫龙", "盐津铺子", "来伊份", "洽洽", "旺旺", "奥利奥",
    "饼干", "糖果", "巧克力", "肉脯", "果冻", "膨化",
    "烘焙", "糕点", "蜜饯", "炒货", "卤味", "休闲食品",
    "预制菜", "锁鲜", "鲜货", "新鲜零食", "短保",
    "量贩", "零食店", "零食连锁",
]


class CninfoCrawler(BaseCrawler):
    name = "巨潮资讯"
    base_url = "http://www.cninfo.com.cn"

    async def fetch(self) -> List[RawItem]:
        items = []
        today = datetime.now()
        start_date = (today - timedelta(days=3)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        try:
            # 1️⃣ 拉深市全量公告 (零食关键词过滤)
            for column in ["szse", "sse"]:
                payload = {
                    "pageSize": 50, "pageNum": 1,
                    "seDate": f"{start_date}~{end_date}",
                    "tabName": "fulltext", "column": column,
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
                            code = ann.get("secCode", "")
                            ann_id = ann.get("announcementId", "")
                            url = f"{self.base_url}/new/disclosure/detail?stockCode={code}&announcementId={ann_id}"

                            is_snack_stock = any(name in sec_name for name in SNACK_STOCKS.values())
                            has_kw = any(kw in title for kw in SNACK_KEYWORDS)
                            if title and (is_snack_stock or has_kw):
                                items.append(RawItem(
                                    source_name=f"巨潮-{sec_name or code}",
                                    title=title, url=url,
                                    published_at=datetime.now(),
                                    raw_content=f"[{column}] {code} {sec_name}",
                                ))
        except Exception as e:
            print(f"  [{self.name}] 全量抓取失败: {str(e)[:60]}")

        # 2️⃣ 逐家上市公司精准抓 (确保核心公司不遗漏)
        headers2 = {**self.headers, "Origin": self.base_url, "Referer": self.base_url + "/"}
        for code, name in SNACK_STOCKS.items():
            try:
                column = "hk" if code.startswith("0") and len(code) == 5 and not code.startswith("00") else "szse"
                if code.startswith("6"): column = "sse"

                payload2 = {
                    "pageSize": 10, "pageNum": 1,
                    "seDate": f"{start_date}~{end_date}",
                    "tabName": "fulltext", "column": column,
                    "category": "", "stock": f"{name},{code}",
                }
                async with httpx.AsyncClient(headers=headers2, timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.post(f"{self.base_url}/new/hisAnnouncement/query", data=payload2)
                    if resp.status_code == 200:
                        data = resp.json()
                        anns2 = data.get("announcements") or []
                        for ann in anns2:
                            title = ann.get("announcementTitle", "").replace("<em>", "").replace("</em>", "")
                            if not title: continue
                            ann_id = ann.get("announcementId", "")
                            c = ann.get("secCode", code)
                            sec_n = ann.get("secName", name)
                            url = f"{self.base_url}/new/disclosure/detail?stockCode={c}&announcementId={ann_id}"
                            if not any(i.url == url for i in items):
                                items.append(RawItem(
                                    source_name=f"巨潮-{sec_n}",
                                    title=title, url=url,
                                    published_at=datetime.now(),
                                    raw_content=f"{sec_n}({c}) 公告",
                                ))
            except Exception as e:
                # 静默，不刷爆日志
                continue

        print(f"  [cninfo] {len(items)} 条 (来自 {len(SNACK_STOCKS)} 家上市公司)")
        return self._limit(items, 60)