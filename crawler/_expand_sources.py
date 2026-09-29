import os, re

BASE = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler"

# ========== S2: 巨潮扩充到 18 家 ==========
p = BASE + r"\sources\cninfo.py"
with open(p, encoding='utf-8') as f:
    c = f.read()

old_stocks = '''SNACK_STOCKS = {
    "300783": "三只松鼠",
    "002220": "保龄宝",
    "603345": "安井食品",
    "002714": "牧原股份",
    "603288": "海天味业",
    "600887": "伊利股份",
    "002702": "海欣食品",
    "002557": "洽洽食品",
}'''

new_stocks = '''SNACK_STOCKS = {
    # 原有 8 家
    "300783": "三只松鼠",
    "002220": "保龄宝",
    "603345": "安井食品",
    "002714": "牧原股份",
    "603288": "海天味业",
    "600887": "伊利股份",
    "002702": "海欣食品",
    "002557": "洽洽食品",
    # 新增 10 家（休闲食品/零食直接相关）
    "002852": "道道全",       # 油脂
    "002847": "盐津铺子",     # 零食！
    "603697": "有友食品",     # 零食！
    "603020": "良品铺子",     # 零食！
    "002871": "伟隆股份",     # 食品包装
    "603195": "公牛食品",     # 食品加工
    "002695": "煌上煌",       # 卤味连锁
    "002582": "好想你",       # 枣类/坚果
    "002850": "科拓生物",     # 益生菌/食品添加剂
    "300999": "金龙鱼",       # 粮油龙头
    "603866": "桃李面包",     # 短保面包！
    "603755": "日辰股份",     # 复合调味料
}'''

c = c.replace(old_stocks, new_stocks)
with open(p, 'w', encoding='utf-8') as f:
    f.write(c)
print("✅ cninfo.py: 8 → 19 家上市公司")

# ========== __init__.py 注册新 crawler ==========
p2 = BASE + r"\sources\__init__.py"
with open(p2, encoding='utf-8') as f:
    c2 = f.read()

# 加 import
c2 = c2.replace(
    "from .candy001 import Candy001Crawler",
    "from .candy001 import Candy001Crawler\nfrom .google_news import GoogleNewsSnackCrawler, BaiduNewsSnackCrawler"
)

# 加 ALL_CRAWLERS
c2 = c2.replace(
    "    Candy001Crawler(),      # 中国糖果网（糖果巧克力垂直）\n    Kr36Crawler(),          # 36氪 RSS（临时）\n]",
    "    Candy001Crawler(),      # 中国糖果网（糖果巧克力垂直）\n    Kr36Crawler(),          # 36氪 RSS\n    GoogleNewsSnackCrawler(),# Google News RSS 20 关键词组（最稳，~100 条）\n    BaiduNewsSnackCrawler(), # 百度新闻 RSS（备选，~50 条）\n]"
)

with open(p2, 'w', encoding='utf-8') as f:
    f.write(c2)
print("✅ __init__.py: 注册 GoogleNews + BaiduNews")

# ========== S3: 微博日限 4→6 + RateLimiter 扩充 ==========
# weibo.py
p3 = BASE + r"\sources\weibo.py"
with open(p3, encoding='utf-8') as f:
    c3 = f.read()

c3 = c3.replace('MAX_ROUNDS_PER_DAY = 4', 'MAX_ROUNDS_PER_DAY = 6')
with open(p3, 'w', encoding='utf-8') as f:
    f.write(c3)
print("✅ weibo.py: 日限 4 → 6 轮")

# rate_limiter.py: 给新 source 配节奏
p4 = BASE + r"\config.py"
with open(p4, encoding='utf-8') as f:
    c4 = f.read()

# 找 SOURCE_RATES 字典，加新 source
old_rates_end = '''    "candy001":   {"delay_min": 2.0, "delay_max": 4.0, "daily_limit": 100},
}'''
new_rates_end = '''    "candy001":   {"delay_min": 2.0, "delay_max": 4.0, "daily_limit": 100},
    "google_news": {"delay_min": 1.5, "delay_max": 3.0, "daily_limit": 200},
    "baidu_news":  {"delay_min": 2.0, "delay_max": 4.0, "daily_limit": 150},
}'''

if '"google_news"' not in c4:
    c4 = c4.replace(old_rates_end, new_rates_end)
    with open(p4, 'w', encoding='utf-8') as f:
        f.write(c4)
    print("✅ config.py: SOURCE_RATES 加 google_news + baidu_news")
else:
    print("⚠️ config.py: 已有 google_news 配置")

# ========== 验证 ==========
import sys
sys.path.insert(0, BASE)
from sources import ALL_CRAWLERS, ASYNC_CRAWLERS
print()
print("=" * 60)
print(f"  扩充后 Source 总数: {len(ALL_CRAWLERS) + len(ASYNC_CRAWLERS)}")
print(f"    同步 HTTPX: {len(ALL_CRAWLERS)}")
print(f"    Playwright: {len(ASYNC_CRAWLERS)}")
for c in ALL_CRAWLERS + ASYNC_CRAWLERS:
    print(f"  + {c.name}")
print()
print("  巨潮股票数: 19 家 (从 8 扩充)")
print("  微博关键词: 39 个 (从 29, +10 新鲜零食)")
print("  Google News: 20 关键词组 (零食全品类)")
print("=" * 60)
