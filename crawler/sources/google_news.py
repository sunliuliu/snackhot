"""Google News RSS —— 多关键词并行搜（最稳定，零反爬）"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sources.base import BaseCrawler
from models import RawItem

# ===== 零食行业关键词矩阵（20 组）=====
SNACK_KEYWORD_GROUPS = [
    # 品牌
    "三只松鼠", "良品铺子", "卫龙", "洽洽", "盐津铺子", "来伊份", "绝味", "周黑鸭",
    # 量贩连锁
    "好想来 零食", "零食很忙", "赵一鸣 零食", "零食代", "老婆大人",
    # 新鲜零食
    "新鲜零食 赛道", "金粒门 鲜货", "锁鲜装 零食", "短保 烘焙", "现做 卤味",
    # 品类
    "魔芋零食", "辣条 新品", "坚果炒货", "糖果巧克力 趋势", "0糖 零食 新品",
    # 事件
    "零食 融资", "休闲食品 年报", "零食 联名", "食品安全 零食",
]

class GoogleNewsSnackCrawler(BaseCrawler):
    name = "google_news"
    base_url = "https://news.google.com/rss/search"

    async def fetch(self):
        import httpx
        import xml.etree.ElementTree as ET
        items = []
        seen_urls = set()

        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
            for kw in SNACK_KEYWORD_GROUPS:
                url = f"https://news.google.com/rss/search?q={kw}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
                try:
                    resp = await self._get(url)
                    if not resp: continue
                    root = ET.fromstring(resp)
                    for item in root.iter('item'):
                        title_el = item.find('title')
                        link_el = item.find('link')
                        pub_el = item.find('pubDate')
                        if title_el is None or link_el is None: continue
                        t = title_el.text or ''
                        l = link_el.text or ''
                        if l in seen_urls or len(t) < 6: continue
                        seen_urls.add(l)
                        items.append(RawItem(
                            source_name="GoogleNews-"+kw[:6],
                            title=t.strip(), url=l.strip(),
                            published_at=pub_el.text if pub_el is not None else None,
                            discovered_at=None, raw_content="", author=None,
                        ))
                    await asyncio.sleep(2.0)  # Google News 限速很松，但稳一点
                except Exception as e:
                    print(f"  [google_news] '{kw}' 失败: {str(e)[:40]}")
        print(f"  [google_news] {len(items)} 条 unique from {len(SNACK_KEYWORD_GROUPS)} 关键词组")
        return items[:120]  # 最多 120 条

# 也加一个百度新闻 RSS（备选）
class BaiduNewsSnackCrawler(BaseCrawler):
    name = "baidu_news"
    base_url = "https://news.baidu.com/rss"

    async def fetch(self):
        import httpx
        import xml.etree.ElementTree as ET
        items = []
        seen_urls = set()
        # 百度新闻 RSS：用百度搜索 RSS
        kws = ["休闲食品", "零食行业", "糖果巧克力", "烘焙食品", "食品加工 零食"]

        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
            for kw in kws:
                url = f"https://news.baidu.com/ns?word={kw}&tn=news&from=news&cl=2&rn=20&ct=1"
                try:
                    resp = await self._get(url)
                    if not resp: continue
                    # 百度新闻页面解析
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp, 'html.parser')
                    for h3 in soup.select('h3.news-title a')[:15]:
                        title = h3.get_text(strip=True)
                        href = h3.get('href', '')
                        if title and len(title) > 6 and href not in seen_urls:
                            seen_urls.add(href)
                            items.append(RawItem(
                                source_name="百度新闻-"+kw[:6],
                                title=title, url=href,
                                published_at=None, discovered_at=None,
                                raw_content="", author=None,
                            ))
                    await asyncio.sleep(2.5)
                except Exception as e:
                    print(f"  [baidu_news] '{kw}' 失败: {str(e)[:40]}")
        print(f"  [baidu_news] {len(items)} 条")
        return items[:80]