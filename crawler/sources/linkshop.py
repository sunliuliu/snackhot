"""联商网 linkshop.com —— 零售行业最权威媒体（GBK 编码）

覆盖：零食量贩、便利店、快消、连锁加盟、食品供应链、即时零售
每天 10-15 条零售/食品相关文章，是行业最核心的媒体信源。
"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx
from .base import BaseCrawler
from models import RawItem

# 宽泛关键词（食品 + 零售）
WIDE_KW = [
    "食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙",
    "辣条","魔芋","奥利奥","烘焙","饼干","糖巧","肉脯","卤味","洽洽",
    "旺旺","绝味","盐津铺子","来伊份","好想来","零食很忙","赵一鸣",
    "休闲食品","食品工业","食品饮料","快消","快消品",
    "便利店","量贩","零食量贩","零食集合店","零食超市",
    "门店","加盟","连锁","供应链","渠道","营销","消费","品牌",
    "即时零售","零售","超市","大卖场","天虹","永辉","盒马","山姆",
    "麦德龙","利群","联华","物美","步步高","家家悦",
    "新鲜零食","零食黑马","零食量贩店","集合店",,

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州",
    # 扩充品牌词库
    "鸣鸣很忙", "零食很忙", "赵一鸣", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "旺旺", "卫龙", "盐津铺子", "绝味", "洽洽", "亿滋", "玛氏", "雀巢", "好时", "百事", "可口可乐", "农夫山泉", "元气森林", "伊利", "蒙牛", "光明", "娃哈哈", "康师傅", "统一", "双汇", "安井", "三全", "思念", "劲仔", "麻辣王子", "甘源", "喜茶", "奈雪的茶", "茶颜悦色", "霸王茶姬", "蜜雪冰城", "古茗", "一点点", "CoCo", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "奥利奥", "大白兔", "徐福记", "达利园", "盼盼", "好丽友", "金丝猴", "马大姐"
]
class LinkshopCrawler(BaseCrawler):
    name = "联商网"
    base_url = "http://www.linkshop.com"

    async def fetch(self) -> List[RawItem]:
        items: List[RawItem] = []
        seen = set()
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout,
                                         follow_redirects=True, verify=False) as client:
                resp = await client.get(f"{self.base_url}/")
                if resp.status_code != 200:
                    return []
                # 强制 GBK 解码（联商网固定用 GBK；httpx 的 resp.text 是只读的！）
                decoded_html = resp.content  # 备用
                for enc in ["gbk", "gb2312", "gb18030", "utf-8"]:
                    try:
                        d = resp.content.decode(enc)
                        if any('\u4e00' <= cc <= '\u9fff' for cc in d[:2000]):
                            decoded_html = d
                            break
                    except Exception:
                        continue
                soup = BeautifulSoup(decoded_html, "lxml")
                for a in soup.find_all("a", href=True):
                    txt = a.get_text(strip=True)
                    href = a.get("href", "")
                    if len(txt) < 15: continue
                    if not (".shtml" in href or "/news/" in href): continue
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
        except Exception as e:
            print(f"  [联商网] 失败: {str(e)[:60]}")
        return self._limit(items, 20)