"""微博搜索爬虫 —— 零食行业 30 关键词

使用 Playwright 持久化浏览器（cookie 已登录保存在 crawler/.weibo_profile/）
首次运行会弹窗让用户登录微博，之后永久有效。

特点：
  ✅ 真实 Chromium 指纹（过微博反爬）
  ✅ 持久化 cookie（登录一次永久有效）
  ✅ 关键词搜索 + 转评赞 + 热度分计算
  ✅ 内置过滤：优惠券/羊毛党/娱乐明星干扰
  ✅ RawItem 标准 6 字段，热度数据嵌入 raw_content JSON
"""
import asyncio, re, json, sys, os, random, hashlib

# 支持环境变量跳过（GitHub Actions 上跑不了，需要本地登录 cookie）
import os as _os
if _os.environ.get('SKIP_WEIBO'):
    raise ImportError('SKIP_WEIBO=1, skipping Playwright weibo crawler')from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# 确保无论从哪里 import 都能找到 base.py 和 models.py
_HERE = os.path.dirname(os.path.abspath(__file__))        # crawler/sources/
_PARENT = os.path.dirname(_HERE)                          # crawler/
os.chdir(_PARENT)
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

# 持久化浏览器目录（crawler/.weibo_profile）
USER_DATA_DIR = str(Path(__file__).resolve().parent.parent / ".weibo_profile")

# ============ 防封保险 ============
MIN_INTERVAL = 0.8       # 最小等待秒
MAX_INTERVAL = 1.6       # 最大等待秒
MAX_ROUNDS_PER_DAY = 6   # 每天最多爬几轮
_state_file = Path(__file__).resolve().parent.parent / ".weibo_state.json"

def _check_daily_limit() -> bool:
    """检查今日是否已达上限"""
    from datetime import datetime as _dt
    today = _dt.now().strftime("%Y-%m-%d")
    try:
        if _state_file.exists():
            st = json.loads(_state_file.read_text())
            if st.get("date") == today and st.get("rounds", 0) >= MAX_ROUNDS_PER_DAY:
                return False
    except:
        pass
    return True

def _record_round():
    """记录今日已爬一轮"""
    from datetime import datetime as _dt
    today = _dt.now().strftime("%Y-%m-%d")
    try:
        if _state_file.exists():
            st = json.loads(_state_file.read_text())
        else:
            st = {}
        if st.get("date") == today:
            st["rounds"] = st.get("rounds", 0) + 1
        else:
            st = {"date": today, "rounds": 1}
        _state_file.write_text(json.dumps(st))
    except:
        pass


# ============ 关键词矩阵 ============

# ============ 新鲜零食赛道（10 个关键词） ============
FRESH_SNACK_QUERIES = [
    {"keyword": "金粒门 鲜货", "category": "新鲜零食"},
    {"keyword": "鲜目录 新鲜零食", "category": "新鲜零食"},
    {"keyword": "新鲜零食 赛道", "category": "新鲜零食"},
    {"keyword": "锁鲜装 零食", "category": "新鲜零食"},
    {"keyword": "短保零食 烘焙", "category": "新鲜零食"},
    {"keyword": "便利店 鲜食 面包", "category": "新鲜零食"},
    {"keyword": "现做卤味 鲜卤", "category": "新鲜零食"},
    {"keyword": "鲜切水果 零食", "category": "新鲜零食"},
    {"keyword": "量贩零食 鲜货", "category": "新鲜零食"},
    {"keyword": "零食集合店 新鲜", "category": "新鲜零食"},
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
    {"keyword": "老婆大人量贩", "category": "渠道变革"},
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
    {"keyword": "零食连锁", "category": "渠道变革"},
    {"keyword": "胖东来零食", "category": "行业观察"},
    {"keyword": "零食联名", "category": "新品发布"},
    {"keyword": "新品发布 零食", "category": "新品发布"},
    {"keyword": "食品安全 零食", "category": "食品安全"},
] + FRESH_SNACK_QUERIES

# ============ 黑名单（过滤无价值内容） ============
NOISE_PATTERNS = [
    r"淘金币", r"拼多多.*5\.9", r"￥\d+.*秒杀", r"薅羊毛", r"白菜",
    r"优惠券", r"返利", r"优惠群", r"小马甲", r"拼夕夕", r"福利价",
    r"明星代言.*零食",  # 代言新闻先保留
]

# 官方账号白名单
OFFICIAL_ACCOUNTS = [
    "来伊份", "三只松鼠", "良品铺子", "洽洽食品官方微博",
    "好想来零食乐园", "零食很忙", "赵一鸣零食",
    "Foodaily每日食品", "零食行业资讯", "联商网",
]






class WeiboCrawler(BaseCrawler):
    """微博关键词搜索爬虫（Playwright 持久化浏览器）"""

    name = "weibo"
    description = f"微博 {len(SEARCH_QUERIES)} 关键词搜索 + 转评赞热度"

    def __init__(self):
        super().__init__()
        if not HAS_PLAYWRIGHT:
            raise ImportError("pip install playwright && python -m playwright install chromium")

    async def fetch(self) -> List[RawItem]:
        """异步爬取所有关键词"""
        if not _check_daily_limit():
            print(f"  ⏰ 今日微博已达上限 ({MAX_ROUNDS_PER_DAY}轮)，跳过", flush=True)
            return []
        _record_round()
        all_items = []

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                viewport={"width": 1440, "height": 900},
                locale="zh-CN",
            )
            await context.add_init_script(
                "Object.defineProperty(navigator,'webdriver',{get:()=>false});window.chrome={runtime:{}};"
            )

            page = context.pages[0] if context.pages else await context.new_page()

            for i, q in enumerate(SEARCH_QUERIES):
                url = f"https://s.weibo.com/weibo?q={q['keyword']}&typeall=1&suball=1"
                try:
                    await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(1200)

                    cur = page.url
                    if "passport" in cur or "login" in cur.lower():
                        print(f"  ⚠️ Cookie 过期（{q['keyword']}），请重新登录", flush=True)
                        break

                    cards = await page.query_selector_all(".card-wrap")
                    print(f"  [{i+1}/{len(SEARCH_QUERIES)}] {q['keyword']}: {len(cards)} 条", flush=True)

                    items = await page.evaluate("""(meta) => {
                        const results = [];
                        document.querySelectorAll('.card-wrap').forEach((c) => {
                            if (c.innerText.includes('推广') || c.innerText.includes('广告')) return;
                            const textEl = c.querySelector('p[node-type*="feed_list_content"], .content, .txt');
                            const text = textEl ? textEl.innerText.trim().replace(/\\n/g, ' ').substring(0, 500) : '';
                            if (!text || text.length < 20) return;
                            const userEl = c.querySelector('.name, a[href*="/u/"][class*="ico"], .m-text-box a');
                            const userName = userEl ? userEl.textContent.trim() : '';
                            const timeEl = c.querySelector('a[href*="/status/"], .from a, a[class*="date"]');
                            const timeText = timeEl ? timeEl.textContent.trim() : '';
                            const link = timeEl ? timeEl.href : '';
                            // 转评赞：遍历所有 a/em/span 找纯数字文本
                            let repost = 0, comment = 0, like = 0;
                            const allEls = c.querySelectorAll('a, em, span, .woo-box-item-flex');
                            const rawNums = new Set();
                            allEls.forEach(el => {
                                let t = el.textContent.trim();
                                t = t.replace(/[\\s,]/g,'');
                                const m = t.match(/^([0-9]+(\\.\\d+)?)([万w])?$/);
                                if (m) {
                                    let v = parseFloat(m[1]);
                                    if (m[3]) v *= 10000;
                                    if (v >= 0 && v < 10000000) rawNums.add(Math.round(v));
                                }
                            });
                            const nums = Array.from(rawNums).sort((a,b)=>b-a);
                            if (nums.length >= 2) { repost = nums[0]; comment = nums[1]; like = nums.length > 2 ? nums[2] : nums[1]; }
                            else if (nums.length === 1) { like = nums[0]; }
                            results.push({ text, userName, timeText, link, repost, comment, like });
                        });
                        return results;
                    }""", q)

                    for it in items:
                        if self._is_noise(it["text"]):
                            continue
                        heat_score = it["repost"] * 3 + it["comment"] * 2 + it["like"]
                        meta_json = json.dumps({
                            "raw_text": it["text"],
                            "repost": it["repost"],
                            "comment": it["comment"],
                            "like": it["like"],
                            "heat_score": heat_score,
                            "keyword": q["keyword"],
                            "category": q["category"],
                        }, ensure_ascii=False)
                        raw = RawItem(
                            source_name=f"微博-{q['keyword']}",
                            title=self._extract_title(it["text"]),
                            url=it["link"],
                            author=it["userName"],
                            published_at=self._parse_time(it["timeText"]),
                            raw_content=meta_json,
                        )
                        all_items.append(raw)

                except Exception as e:
                    print(f"  ❌ {q['keyword']}: {str(e)[:50]}", flush=True)
                    continue

                await page.wait_for_timeout(int(random.uniform(MIN_INTERVAL, MAX_INTERVAL) * 1000))

            await context.close()

        unique = self._dedupe(all_items)
        print(f"\\n📊 微博总计: {len(all_items)} → 过滤后 {len(unique)} 条有效", flush=True)
        return unique

    def _is_noise(self, text: str) -> bool:
        for pat in NOISE_PATTERNS:
            if re.search(pat, text):
                return True
        return len(text) < 40

    def _extract_title(self, text: str) -> str:
        # 去掉开头的 "c 用户名" 之类的用户名前缀（微博 DOM 解析出来带的）
        clean = re.sub(r"^c\s+\S+\s+", "", text).strip()
        clean = re.sub(r"@\S+\s*", "", clean)      # 去掉 @人
        clean = re.sub(r"#([^#]+)#", "", clean).strip()  # 去掉话题 tag
        clean = re.sub(r"\\s+", " ", clean).strip()
        return clean[:70] + ("..." if len(clean) > 70 else "")

    def _parse_time(self, t: str) -> Optional[datetime]:
        now = datetime.now()
        try:
            if "分钟前" in t:
                return now - timedelta(minutes=int(re.search(r"(\\d+)", t).group(1)))
            elif "小时前" in t:
                return now - timedelta(hours=int(re.search(r"(\\d+)", t).group(1)))
            elif "今天" in t:
                m = re.search(r"(\\d+)[.:](\\d+)", t)
                if m: return now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0)
            elif "昨天" in t:
                m = re.search(r"(\\d+)[.:](\\d+)", t)
                if m: return (now - timedelta(days=1)).replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0)
            elif re.match(r"\\d+月\\d+日", t):
                m = re.match(r"(\\d+)月(\\d+)日", t)
                if m: return now.replace(month=int(m.group(1)), day=int(m.group(2)))
        except:
            pass
        return None

    def _dedupe(self, items: List[RawItem]) -> List[RawItem]:
        seen = set()
        unique = []
        for it in items:
            key = it.title[:30]
            if key not in seen:
                seen.add(key)
                unique.append(it)
        unique.sort(key=lambda x: self._get_heat(x), reverse=True)
        return unique

    def _get_heat(self, item: RawItem) -> int:
        try:
            meta = json.loads(item.raw_content) if item.raw_content else {}
            return meta.get("heat_score", 0)
        except:
            return 0


if __name__ == "__main__":
    async def test():
        src = WeiboCrawler()
        items = await src.fetch()
        print(f"\\n=== Top 10 by heat_score ===")
        for it in items[:10]:
            try: meta = json.loads(it.raw_content) if it.raw_content else {}
            except: meta = {}
            print(f"  🔥{meta.get('heat_score',0):>5}  [{it.source_name}] {it.title[:50]}")
    asyncio.run(test())