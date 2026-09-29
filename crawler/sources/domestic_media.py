"""
国内新闻源（替换 Google News RSS，零墙）:
  1. 澎湃新闻 thepaper.cn （食品饮料频道）
  2. 食品商务网 21food.cn （行业资讯）
  3. 中国经济网 ce.cn （食品板块）
  4. 36氪 food.36kr.com （食品餐饮频道）
全 HTTPX 静态爬，无反爬，秒级稳定。
"""
import asyncio, sys, os, re
from typing import List
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sources.base import BaseCrawler
from models import RawItem

# 关键词过滤（泛用：标题/摘要必须命中食品/零食相关）
FOOD_KW = [
    '食品', '零食', '休闲', '糖果', '巧克力', '坚果', '炒货', '卤味', '肉脯',
    '饼干', '糕点', '烘焙', '面包', '饮料', '饮品', '乳品', '鲜奶', '冰淇淋',
    '雪糕', '辣条', '魔芋', '薯片', '膨化', '蜜饯', '果干', '罐头', '方便',
    '三只松鼠', '良品铺子', '卫龙', '洽洽', '盐津铺子', '来伊份', '绝味', '周黑鸭',
    '安井', '海天', '伊利', '金龙鱼', '桃李', '钟薛高', '元气森林',
    '好想来', '零食很忙', '赵一鸣', '量贩', '连锁', '金粒门', '鲜货', '新鲜零食',
]

def _is_food_related(text: str) -> bool:
    if not text: return False
    t = text.lower()
    return any(k.lower() in t for k in FOOD_KW)


class ThepaperCrawler(BaseCrawler):
    """澎湃新闻 - 食品饮料频道"""
    name = "thepaper"
    base_url = "https://www.thepaper.cn"
    crawl_urls = [
        "https://www.thepaper.cn/channel_25951",  # 食品饮料
        "https://www.thepaper.cn/channel_25950",  # 消费
    ]

    async def fetch(self) -> List[RawItem]:
        import httpx
        from bs4 import BeautifulSoup
        items = []
        seen = set()
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as c:
            for url in self.crawl_urls:
                try:
                    resp = await self._get(url)
                    if not resp: continue
                    soup = BeautifulSoup(resp, 'html.parser')
                    for a in soup.select('a[href*="newsDetail"], a[href*="news_"], .news_li a'):
                        title = a.get_text(strip=True)
                        href = a.get('href', '')
                        if title and len(title) > 8 and _is_food_related(title):
                            full = href if href.startswith('http') else self.base_url + href
                            if full not in seen:
                                seen.add(full)
                                items.append(RawItem(
                                    source_name="澎湃新闻", title=title, url=full,
                                    published_at=None, discovered_at=None, raw_content="", author=None,
                                ))
                    await asyncio.sleep(1.5)
                except Exception as e:
                    print(f"  [thepaper] {url} 失败: {str(e)[:50]}")
        print(f"  [thepaper] {len(items)} 条")
        return items[:40]


class Food21Crawler(BaseCrawler):
    """食品商务网 - 行业资讯（零食/休闲食品）"""
    name = "food21"
    base_url = "https://news.21food.cn"
    crawl_urls = [
        "https://news.21food.cn/list-1.html",       # 全部资讯
        "https://news.21food.cn/list-43.html",      # 休闲食品
        "https://news.21food.cn/list-62.html",      # 糖果巧克力
        "https://news.21food.cn/list-3.html",       # 烘焙食品
    ]

    async def fetch(self) -> List[RawItem]:
        import httpx
        from bs4 import BeautifulSoup
        items = []
        seen = set()
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as c:
            for url in self.crawl_urls:
                try:
                    resp = await self._get(url)
                    if not resp: continue
                    soup = BeautifulSoup(resp, 'html.parser')
                    for a in soup.select('a[href*="html"], .list_item a, .news-list a'):
                        title = a.get_text(strip=True)
                        href = a.get('href', '')
                        if title and len(title) > 6 and _is_food_related(title):
                            full = href if href.startswith('http') else self.base_url + '/' + href.lstrip('/')
                            if full not in seen:
                                seen.add(full)
                                items.append(RawItem(
                                    source_name="食品商务网", title=title, url=full,
                                    published_at=None, discovered_at=None, raw_content="", author=None,
                                ))
                    await asyncio.sleep(1.5)
                except Exception as e:
                    print(f"  [food21] {url} 失败: {str(e)[:50]}")
        print(f"  [food21] {len(items)} 条")
        return items[:50]


class CeCrawler(BaseCrawler):
    """中国经济网 - 食品板块"""
    name = "ce_cn"
    base_url = "http://www.ce.cn"
    crawl_urls = [
        "http://www.ce.cn/cysc/sp/",               # 食品
        "http://www.ce.cn/cysc/sp/shipin/",        # 食品工业
    ]

    async def fetch(self) -> List[RawItem]:
        import httpx
        from bs4 import BeautifulSoup
        items = []
        seen = set()
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as c:
            for url in self.crawl_urls:
                try:
                    resp = await self._get(url)
                    if not resp: continue
                    soup = BeautifulSoup(resp, 'html.parser')
                    for a in soup.select('a'):
                        title = a.get_text(strip=True)
                        href = a.get('href', '')
                        if title and len(title) > 10 and _is_food_related(title) and href.endswith('.shtml'):
                            full = href if href.startswith('http') else self.base_url + href
                            if full not in seen:
                                seen.add(full)
                                items.append(RawItem(
                                    source_name="中国经济网", title=title, url=full,
                                    published_at=None, discovered_at=None, raw_content="", author=None,
                                ))
                    await asyncio.sleep(1.5)
                except Exception as e:
                    print(f"  [ce_cn] {url} 失败: {str(e)[:50]}")
        print(f"  [ce_cn] {len(items)} 条")
        return items[:40]