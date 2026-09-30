"""中国食品安全网 cfsn.cn — 食品安全 + 市场监管权威平台

覆盖：食品安全、抽检通报、市场监管政策、消费者权益
是监管动态、召回、风险预警的第一信源
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
    "绝味","盐津铺子","来伊份","零食","休闲食品","食品饮料",
    "安全","监管","抽检","召回","国标","食品添加剂","市场监管","消费者",
    "中毒","问题","不合格","通报","处罚","风险","预警","辟谣",
    "投诉","曝光","维权","黑榜","红榜","打假","假冒伪劣","防腐剂","超标",,

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州",
    # 扩充品牌词库
    "鸣鸣很忙", "零食很忙", "赵一鸣", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "旺旺", "卫龙", "盐津铺子", "绝味", "洽洽", "亿滋", "玛氏", "雀巢", "好时", "百事", "可口可乐", "农夫山泉", "元气森林", "伊利", "蒙牛", "光明", "娃哈哈", "康师傅", "统一", "双汇", "安井", "三全", "思念", "劲仔", "麻辣王子", "甘源", "喜茶", "奈雪的茶", "茶颜悦色", "霸王茶姬", "蜜雪冰城", "古茗", "一点点", "CoCo", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "奥利奥", "大白兔", "徐福记", "达利园", "盼盼", "好丽友", "金丝猴", "马大姐"
]
class CfsnCrawler(BaseCrawler):
    name = "中国食品安全网"
    base_url = "https://www.cfsn.cn"
    crawl_urls = [
        "https://www.cfsn.cn/index.html",
        "https://www.cfsn.cn/news/22.html",      # 要闻
        "https://www.cfsn.cn/news/2369.html",   # 监管
        "https://www.cfsn.cn/news/2371.html",   # 市场
        "https://www.cfsn.cn/news/2372.html",   # 质量
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
                        # cfsn 有 GBK 编码的页面
                        html = resp.text
                        if 'charset="gbk"' in html.lower() or "charset='gbk'" in html.lower():
                            try: html = resp.content.decode("gbk", errors="ignore")
                            except: pass
                        soup = BeautifulSoup(html, "lxml")
                        for a in soup.find_all("a", href=True):
                            txt = a.get_text(strip=True)
                            href = a.get("href", "")
                            if len(txt) < 10: continue
                            if not ("/news/detail/" in href or "/news/" in href): continue
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
            print(f"  [中国食品安全网] 失败: {str(e)[:60]}")
        return self._limit(items, 25)
