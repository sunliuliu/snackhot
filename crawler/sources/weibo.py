"""微博搜索爬虫 —— 零食行业关键词（三模式自动切换）

模式自动检测（优先级从上到下）:
  1. COOKIE_STRING 模式: 环境变量 WEIBO_COOKIE 存在 → httpx 请求 m.weibo.cn JSON 接口
     - GitHub Actions 可用，cookie 存 Secret
     - 优点：不需要 Playwright，速度快
     - 缺点：微博 cookie 几小时过期，需要手动更新
  2. PLAYWRIGHT_PERSIST 模式: Playwright 已装 + crawler/.weibo_profile/ 存在
     - 本地跑用，cookie 持久化在浏览器 profile
     - 优点：最稳定，过反爬
  3. SKIP 模式: 无 cookie 无 playwright → 返回空数组 + 打印 skip 日志
     - 不 raise ImportError，不中断主流程

关键词矩阵：30+ 零食相关关键词，带分类标注
"""
import asyncio, re, json, sys, os, random, hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)
sys.path.insert(0, _PARENT)

try:
    from .base import BaseCrawler
    from ..models import RawItem
except (ImportError, ValueError):
    from base import BaseCrawler
    from models import RawItem

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

import httpx
from bs4 import BeautifulSoup

# ============ 配置 ============
USER_DATA_DIR = str(Path(__file__).resolve().parent.parent / ".weibo_profile")
WEIBO_COOKIE_STR = os.environ.get("WEIBO_COOKIE", "").strip()
WEIBO_MODE = os.environ.get("WEIBO_MODE", "").strip().lower()

# ============ 防封保险 ============
MIN_INTERVAL = 1.0
MAX_INTERVAL = 2.2
MAX_ROUNDS_PER_DAY = 8
_state_file = Path(__file__).resolve().parent.parent / ".weibo_state.json"

def _check_daily_limit() -> bool:
    try:
        if _state_file.exists():
            st = json.loads(_state_file.read_text())
            today = datetime.now().strftime("%Y-%m-%d")
            if st.get("date") == today and st.get("rounds", 0) >= MAX_ROUNDS_PER_DAY:
                return False
    except: pass
    return True

def _record_round():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        st = {}
        if _state_file.exists():
            st = json.loads(_state_file.read_text())
        st["date"] = today
        st["rounds"] = st.get("rounds", 0) + 1
        _state_file.write_text(json.dumps(st))
    except: pass


# ============ 关键词矩阵 ============
FRESH_SNACK_QUERIES = [
    {"keyword": "金粒门 鲜货", "category": "新鲜零食"},
    {"keyword": "鲜目录 新鲜零食", "category": "新鲜零食"},
    {"keyword": "新鲜零食 赛道", "category": "新鲜零食"},
    {"keyword": "锁鲜装 零食", "category": "新鲜零食"},
    {"keyword": "短保零食 烘焙", "category": "新鲜零食"},
    {"keyword": "现做卤味 鲜卤", "category": "新鲜零食"},
    {"keyword": "鲜切水果 零食", "category": "新鲜零食"},
    {"keyword": "量贩零食 鲜货", "category": "新鲜零食"},
]

SEARCH_QUERIES = [
    {"keyword": "三只松鼠", "category": "品牌动态"},
    {"keyword": "良品铺子", "category": "品牌动态"},
    {"keyword": "卫龙食品", "category": "品牌动态"},
    {"keyword": "盐津铺子", "category": "品牌动态"},
    {"keyword": "洽洽食品", "category": "品牌动态"},
    {"keyword": "来伊份", "category": "品牌动态"},
    {"keyword": "绝味食品", "category": "品牌动态"},
    {"keyword": "旺旺集团", "category": "品牌动态"},
    {"keyword": "好想来零食", "category": "渠道变革"},
    {"keyword": "零食很忙", "category": "渠道变革"},
    {"keyword": "赵一鸣零食", "category": "渠道变革"},
    {"keyword": "零食代连锁", "category": "渠道变革"},
    {"keyword": "零食集合店", "category": "渠道变革"},
    {"keyword": "魔芋零食", "category": "品类趋势"},
    {"keyword": "辣条", "category": "品类趋势"},
    {"keyword": "坚果炒货", "category": "品类趋势"},
    {"keyword": "肉脯卤味", "category": "品类趋势"},
    {"keyword": "糖果巧克力", "category": "品类趋势"},
    {"keyword": "饼干烘焙", "category": "品类趋势"},
    {"keyword": "0糖0添加食品", "category": "品类趋势"},
    {"keyword": "新消费零食", "category": "品类趋势"},
    {"keyword": "零食行业", "category": "行业观察"},
    {"keyword": "量贩零食", "category": "渠道变革"},
    {"keyword": "休闲食品", "category": "品类趋势"},
    {"keyword": "胖东来零食", "category": "行业观察"},
    {"keyword": "零食联名", "category": "新品发布"},
    {"keyword": "新品发布 零食", "category": "新品发布"},
    {"keyword": "食品安全 零食", "category": "食品安全"},
    {"keyword": "预制菜 零食", "category": "品类趋势"},
    {"keyword": "零食连锁", "category": "渠道变革"},
] + FRESH_SNACK_QUERIES

NOISE_PATTERNS = [
    r"淘金币", r"拼多多.*5\.9", r"￥\d+.*秒杀", r"薅羊毛", r"白菜",
    r"优惠券", r"返利", r"优惠群", r"拼夕夕", r"福利价", r"抽奖",
    r"粉丝福利", r"转发送",
]

OFFICIAL_ACCOUNTS = [
    "来伊份", "三只松鼠", "良品铺子", "洽洽食品官方微博",
    "好想来零食乐园", "零食很忙", "赵一鸣零食",
    "Foodaily每日食品", "零食行业资讯", "联商网",
]


# ============ 模式选择 ============
def _detect_mode() -> str:
    """返回 'httpx' / 'playwright' / 'skip'"""
    # 强制模式
    if WEIBO_MODE in ('httpx', 'cookie') and WEIBO_COOKIE_STR:
        return 'httpx'
    if WEIBO_MODE in ('playwright', 'pw') and HAS_PLAYWRIGHT and os.path.isdir(USER_DATA_DIR):
        return 'playwright'
    if WEIBO_MODE == 'skip':
        return 'skip'

    # 自动检测
    if WEIBO_COOKIE_STR:
        return 'httpx'
    if HAS_PLAYWRIGHT and os.path.isdir(USER_DATA_DIR):
        return 'playwright'
    return 'skip'


class WeiboCrawler(BaseCrawler):
    """微博关键词搜索爬虫（三模式自动切换: httpx+cookie / Playwright / skip）"""
    name = "weibo"
    description = f"微博 {len(SEARCH_QUERIES)} 关键词搜索 ({_detect_mode()} 模式)"

    def __init__(self):
        super().__init__()
        self.mode = _detect_mode()

    # ============ 主入口 ============
    async def fetch(self) -> List[RawItem]:
        if self.mode == 'skip':
            print("  [weibo] ⏭️ skip (no WEIBO_COOKIE env or Playwright profile). Set WEIBO_COOKIE or .weibo_profile/ to enable.")
            return []
        if not _check_daily_limit():
            print(f"  [weibo] ⏰ 今日已达上限 ({MAX_ROUNDS_PER_DAY}轮)")
            return []

        _record_round()
        print(f"  [weibo] 🚀 {self.mode} 模式, {len(SEARCH_QUERIES)} 关键词")

        if self.mode == 'httpx':
            items = await self._fetch_httpx()
        else:
            items = await self._fetch_playwright()

        unique = self._dedupe(items)
        print(f"  [weibo] 📊 总计 {len(items)} → 去重后 {len(unique)} 条")
        return unique

    # ============ httpx + cookie 模式 ============
    async def _fetch_httpx(self) -> List[RawItem]:
        """用 httpx 请求 m.weibo.cn 移动版 JSON 接口"""
        import urllib.parse
        items = []
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 MicroMessenger/8.0.38",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://m.weibo.cn/",
            "Cookie": WEIBO_COOKIE_STR,
            "X-Requested-With": "XMLHttpRequest",
        }

        async with httpx.AsyncClient(headers=headers, timeout=20, follow_redirects=True) as c:
            for i, q in enumerate(SEARCH_QUERIES):
                keyword = q['keyword']
                encoded = urllib.parse.quote(keyword)
                url = f"https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D{encoded}&page_type=searchall"
                try:
                    resp = await c.get(url)
                    if resp.status_code != 200:
                        print(f"  [{i+1}/{len(SEARCH_QUERIES)}] {keyword}: HTTP {resp.status_code}")
                        continue
                    data = resp.json()
                    if data.get('ok') != 1:
                        print(f"  [{i+1}/{len(SEARCH_QUERIES)}] {keyword}: api ok != 1 (可能 cookie 过期)")
                        continue
                    cards = data.get('data', {}).get('cards', [])
                    count = 0
                    for card in cards:
                        if card.get('card_type') == 9:
                            mblog = card.get('mblog', {})
                            text = mblog.get('text', '')
                            # 去除 HTML 标签
                            text = BeautifulSoup(text, 'html.parser').get_text(strip=True)
                            if not text or len(text) < 20:
                                continue
                            if self._is_noise(text):
                                continue

                            user = mblog.get('user', {}).get('screen_name', '')
                            bid = mblog.get('bid', '')
                            reposts_count = mblog.get('reposts_count', 0)
                            comments_count = mblog.get('comments_count', 0)
                            attitudes_count = mblog.get('attitudes_count', 0)
                            heat_score = reposts_count * 3 + comments_count * 2 + attitudes_count

                            created_at = mblog.get('created_at', '')
                            published = self._parse_api_time(created_at)

                            raw_item = RawItem(
                                source_name=f"微博-{keyword}",
                                title=self._extract_title(text),
                                url=f"https://m.weibo.cn/detail/{bid}" if bid else "",
                                author=user,
                                published_at=published,
                                raw_content=json.dumps({
                                    "raw_text": text,
                                    "repost": reposts_count,
                                    "comment": comments_count,
                                    "like": attitudes_count,
                                    "heat_score": heat_score,
                                    "keyword": keyword,
                                    "category": q["category"],
                                    "mode": "httpx_cookie",
                                }, ensure_ascii=False),
                            )
                            items.append(raw_item)
                            count += 1

                    print(f"  [{i+1}/{len(SEARCH_QUERIES)}] {keyword}: {count} 条", flush=True)

                except Exception as e:
                    print(f"  [{i+1}/{len(SEARCH_QUERIES)}] {keyword}: {str(e)[:50]}")

                await asyncio.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

        return items

    def _parse_api_time(self, t: str) -> Optional[datetime]:
        """微博 API 返回的 created_at 格式: 'Tue Sep 30 15:30:00 +0800 2026'"""
        if not t: return None
        try:
            # 尝试 ISO 格式
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(t).replace(tzinfo=None)
        except: pass
        try:
            # 手动解析
            import re
            m = re.match(r'\w+\s+(\w+)\s+(\d+)\s+(\d+):(\d+):\d+\s+\+\d+\s+(\d+)', t)
            if m:
                month_str, day, hour, minute, year = m.groups()
                months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
                return datetime(int(year), months.get(month_str, 1), int(day), int(hour), int(minute))
        except: pass
        return None

    # ============ Playwright 持久化模式 (本地) ============
    async def _fetch_playwright(self) -> List[RawItem]:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36",
                viewport={"width": 1440, "height": 900},
                locale="zh-CN",
            )
            await context.add_init_script(
                "Object.defineProperty(navigator,'webdriver',{get:()=>false});window.chrome={runtime:{}};"
            )

            page = context.pages[0] if context.pages else await context.new_page()
            items = []

            for i, q in enumerate(SEARCH_QUERIES):
                url = f"https://s.weibo.com/weibo?q={q['keyword']}&typeall=1&suball=1"
                try:
                    await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(1200)
                    cur = page.url
                    if "passport" in cur or "login" in cur.lower():
                        print(f"  [weibo] ⚠️ cookie 过期 ({q['keyword']}), 请重新登录 .weibo_profile/")
                        break

                    cards = await page.query_selector_all(".card-wrap")
                    count = 0
                    for c in cards:
                        textEl = await c.query_selector('p[node-type*="feed_list_content"], .content, .txt')
                        if not textEl: continue
                        text = (await textEl.inner_text()).strip().replace("\n", " ")[:500]
                        if not text or len(text) < 20 or self._is_noise(text): continue

                        userEl = await c.query_selector('.name, a[href*="/u/"]')
                        userName = (await userEl.inner_text()).strip() if userEl else ""
                        timeEl = await c.query_selector('a[href*="/status/"], .from a')
                        timeText = (await timeEl.inner_text()).strip() if timeEl else ""
                        link = await timeEl.get_attribute('href') if timeEl else ""

                        # 转评赞提取
                        nums = []
                        for sel in ['.woo-like-count', '.woo-comment', '.woo-forward']:
                            el = await c.query_selector(sel)
                            if el:
                                t = (await el.inner_text()).strip()
                                t = re.sub(r'[^\d.]', '', t)
                                if t:
                                    try: nums.append(float(t))
                                    except: pass

                        heat = (nums[0]*3 + nums[1]*2 + nums[2]) if len(nums) >= 3 else 0

                        raw_item = RawItem(
                            source_name=f"微博-{q['keyword']}",
                            title=self._extract_title(text),
                            url=link or "",
                            author=userName,
                            published_at=self._parse_time(timeText),
                            raw_content=json.dumps({
                                "raw_text": text, "heat_score": heat,
                                "keyword": q["keyword"], "category": q["category"],
                                "mode": "playwright_persist",
                            }, ensure_ascii=False),
                        )
                        items.append(raw_item)
                        count += 1

                    print(f"  [{i+1}/{len(SEARCH_QUERIES)}] {q['keyword']}: {count} 条")
                except Exception as e:
                    print(f"  ❌ {q['keyword']}: {str(e)[:50]}")

                await asyncio.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

            await context.close()

        return items

    # ============ 通用辅助 ============
    def _is_noise(self, text: str) -> bool:
        for pat in NOISE_PATTERNS:
            if re.search(pat, text): return True
        return len(text) < 40

    def _extract_title(self, text: str) -> str:
        clean = re.sub(r"^c\s+\S+\s+", "", text).strip()
        clean = re.sub(r"@\S+\s*", "", clean)
        clean = re.sub(r"#([^#]+)#", "", clean).strip()
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean[:70] + ("..." if len(clean) > 70 else "")

    def _parse_time(self, t: str) -> Optional[datetime]:
        now = datetime.now()
        try:
            if "分钟前" in t: return now - timedelta(minutes=int(re.search(r"(\d+)", t).group(1)))
            elif "小时前" in t: return now - timedelta(hours=int(re.search(r"(\d+)", t).group(1)))
            elif "今天" in t:
                m = re.search(r"(\d+)[.:](\d+)", t)
                if m: return now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0)
            elif "昨天" in t:
                m = re.search(r"(\d+)[.:](\d+)", t)
                if m: return (now - timedelta(days=1)).replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0)
        except: pass
        return None

    def _dedupe(self, items: List[RawItem]) -> List[RawItem]:
        seen = set(); unique = []
        for it in items:
            key = it.title[:30]
            if key not in seen:
                seen.add(key); unique.append(it)
        unique.sort(key=lambda x: self._get_heat(x), reverse=True)
        return unique

    def _get_heat(self, item: RawItem) -> int:
        try:
            meta = json.loads(item.raw_content) if item.raw_content else {}
            return meta.get("heat_score", 0)
        except: return 0


if __name__ == "__main__":
    async def test():
        src = WeiboCrawler()
        items = await src.fetch()
        print(f"\n=== Top 10 by heat_score ===")
        for it in items[:10]:
            try: meta = json.loads(it.raw_content) if it.raw_content else {}
            except: meta = {}
            print(f"  🔥{meta.get('heat_score',0):>5}  [{it.source_name}] {it.title[:50]}")
    asyncio.run(test())
