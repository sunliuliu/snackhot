"""
国内新闻源（替换 Google News RSS，零墙）:
  1. 澎湃新闻 thepaper.cn （食品饮料 + 消费 + 财经多频道交叉）
  2. 食品商务网 21food.cn （JS 动态渲染，通过 RSSHub 桥接 + 多实例 fallback）
  3. 中国经济网 ce.cn （食品板块）
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
    '食品安全', '食品工业', '食品质量', '农产品', '预制菜', '生鲜',
    '消费', '餐饮', '奶茶', '咖啡', '酒',,

    # 零食连锁/食品品牌扩充
"鸣鸣很忙", "零食很忙", "赵一鸣", "赵一鸣零食", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "良品", "旺旺", "旺旺集团", "卫龙", "盐津铺子", "绝味", "绝味食品", "洽洽", "洽洽食品", "奥利奥", "亿滋", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "麻辣王子", "劲仔", "飞旺", "玉峰", "金大州",
    # 扩充品牌词库
    "鸣鸣很忙", "零食很忙", "赵一鸣", "好想来", "老婆大人", "来优品", "吖嘀吖嘀", "陆小馋", "万辰集团", "良品铺子", "三只松鼠", "来伊份", "薛记炒货", "旺旺", "卫龙", "盐津铺子", "绝味", "洽洽", "亿滋", "玛氏", "雀巢", "好时", "百事", "可口可乐", "农夫山泉", "元气森林", "伊利", "蒙牛", "光明", "娃哈哈", "康师傅", "统一", "双汇", "安井", "三全", "思念", "劲仔", "麻辣王子", "甘源", "喜茶", "奈雪的茶", "茶颜悦色", "霸王茶姬", "蜜雪冰城", "古茗", "一点点", "CoCo", "零食有鸣", "糖巢", "零食优选", "爱零食", "戴永红", "奥利奥", "大白兔", "徐福记", "达利园", "盼盼", "好丽友", "金丝猴", "马大姐"
]
def _is_food_related(text: str) -> bool:
    if not text: return False
    t = text.lower()
    return any(k.lower() in t for k in FOOD_KW)


class ThepaperCrawler(BaseCrawler):
    """澎湃新闻 - 食品饮料 + 消费 + 财经多频道交叉"""
    name = "thepaper"
    base_url = "https://www.thepaper.cn"
    crawl_urls = [
        "https://www.thepaper.cn/channel_25951",  # 食品饮料
        "https://www.thepaper.cn/channel_25950",  # 消费
        "https://www.thepaper.cn/channel_25952",  # 财经
    ]

    async def fetch(self) -> List[RawItem]:
        import httpx
        from bs4 import BeautifulSoup
        items = []
        seen = set()
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as c:
            for url in self.crawl_urls:
                try:
                    resp = await c.get(url)
                    if resp.status_code != 200: continue
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for a in soup.select('a[href*="newsDetail"]'):
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
                    await asyncio.sleep(1.0)
                except Exception as e:
                    print(f"  [thepaper] {url} 失败: {str(e)[:50]}")
        print(f"  [thepaper] {len(items)} 条")
        return items[:40]


# RSSHub 公开实例列表 (按优先级 fallback)
RSSHUB_INSTANCES = [
    "https://rsshub.rssforever.com",
    "https://rsshub.app",
]

class Food21Crawler(BaseCrawler):
    """食品商务网 - RSSHub 桥接 + 多实例 fallback"""
    name = "food21"
    base_url = "https://news.21food.cn"
    # 内部路由模板
    _rss_routes = [
        "/21food/news/list-1",     # 全部资讯
        "/21food/news/list-43",    # 休闲食品
        "/21food/news/list-62",    # 糖果巧克力
    ]

    async def fetch(self) -> List[RawItem]:
        import httpx
        from bs4 import BeautifulSoup
        items = []
        seen = set()

        async with httpx.AsyncClient(headers=self.headers, timeout=15, follow_redirects=True) as c:
            for route in self._rss_routes:
                # 尝试每个 RSSHub 实例
                resp = None
                for instance in RSSHUB_INSTANCES:
                    url = instance + route
                    try:
                        r = await c.get(url)
                        if r.status_code == 200 and len(r.text) > 300 and '<title>' in r.text:
                            resp = r
                            break
                    except Exception:
                        continue

                if not resp:
                    print(f"  [food21] {route}: 所有 RSSHub 实例都失败 (跳过)")
                    continue

                # RSS 解析
                soup = BeautifulSoup(resp.text, 'xml')
                for item in soup.find_all('item'):
                    title_el = item.find('title')
                    link_el = item.find('link')
                    if not title_el or not link_el: continue
                    title = title_el.get_text(strip=True)
                    link = link_el.get_text(strip=True)
                    if title and len(title) > 6 and _is_food_related(title):
                        if link not in seen:
                            seen.add(link)
                            items.append(RawItem(
                                source_name="食品商务网", title=title, url=link,
                                published_at=None, discovered_at=None, raw_content="", author=None,
                            ))
                await asyncio.sleep(1.0)

        print(f"  [food21] {len(items)} 条")
        return items[:50]


class CeCrawler(BaseCrawler):
    """中国经济网 - 食品板块"""
    name = "ce_cn"
    base_url = "http://www.ce.cn"
    crawl_urls = [
        "http://www.ce.cn/cysc/sp/",               # 食品
    ]

    async def fetch(self) -> List[RawItem]:
        import httpx
        from bs4 import BeautifulSoup
        items = []
        seen = set()
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as c:
            for url in self.crawl_urls:
                try:
                    resp = await c.get(url)
                    if resp.status_code != 200: continue
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for a in soup.select('a'):
                        title = a.get_text(strip=True)
                        href = a.get('href', '')
                        if title and len(title) > 10 and _is_food_related(title) and (href.endswith('.shtml') or '/cysc/' in href):
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
