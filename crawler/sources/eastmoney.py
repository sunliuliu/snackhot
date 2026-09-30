"""东方财富 - 食品饮料相关新闻（宽泛关键词过滤 + 让 LLM 做零食判定）"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx, re
from .base import BaseCrawler
from models import RawItem

# 宽泛食品饮料关键词（先预过滤砍 80% 不相关内容，再交给 LLM 做零食判定）
# 注意：这是"食品饮料行业"大类，不是"零食"子类
WIDE_FOOD_KW = [
    # 食品饮料大类
    "食品", "饮料", "乳业", "乳品", "白酒", "啤酒", "红酒", "红酒", "黄酒",
    # 零食品类
    "零食", "坚果", "糖果", "巧克力", "饼干", "糕点", "膨化", "果冻",
    "肉脯", "卤味", "辣条", "魔芋", "蜜饯", "炒货", "糖巧",
    # 头部品牌
    "三只松鼠", "良品铺子", "百草味", "卫龙", "盐津铺子", "来伊份",
    "洽洽", "旺旺", "奥利奥", "亿滋", "玛氏", "雀巢", "费列罗", "好丽友",
    "卡夫", "联合利华", "亨氏", "康师傅", "统一",
    # 零食量贩零售
    "好想来", "零食很忙", "赵一鸣", "零食代", "怡佳仁", "贪吃嘴",
    "量贩零食", "零食集合店", "零食超市",
    # 行业通用
    "休闲食品", "食品工业", "食品饮料", "食品加工业", "食品制造业",
    "食品安全", "抽检", "召回", "添加剂", "国标", "防腐剂",
    "预包装食品", "预制菜", "方便食品",,

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州"
]
URLS = [
    ("财经要闻", "https://finance.eastmoney.com/a/cyyzsp.html"),
    ("公司新闻", "https://finance.eastmoney.com/a/cgsxw.html"),
    ("财经滚动", "https://finance.eastmoney.com/a/ccjxw.html"),
]

class EastmoneyCrawler(BaseCrawler):
    name = "东方财富"

    async def fetch(self) -> List[RawItem]:
        items: List[RawItem] = []
        seen = set()
        filtered_out = 0
        for label, url in URLS:
            try:
                async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        continue
                    soup = BeautifulSoup(resp.text, "lxml")
                    for li in soup.select("ul.newsListContent li, #newsListContent li"):
                        a = li.find("a") if li.name == "li" else li
                        if not a:
                            continue
                        title = a.get_text(strip=True)
                        href = a.get("href", "")
                        if not title or len(title) < 10 or not "/a/" in href:
                            continue
                        if href.startswith("//"):
                            href = "https:" + href
                        elif href.startswith("/"):
                            href = "https://finance.eastmoney.com" + href
                        # 宽泛预过滤：必须包含食品饮料关键词
                        if not any(kw in title for kw in WIDE_FOOD_KW):
                            filtered_out += 1
                            continue
                        key = href.split("?")[0]
                        if key in seen:
                            continue
                        seen.add(key)
                        items.append(RawItem(
                            source_name=f"东财-{label}",
                            title=title, url=href,
                            published_at=datetime.now(),
                        ))
            except Exception as e:
                print(f"  [东财] {label} 失败: {str(e)[:50]}")
        print(f"    宽泛过滤: 保留 {len(items)} 条, 过滤 {filtered_out} 条非食品内容")
        return self._limit(items, 30)