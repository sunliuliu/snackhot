"""诊断腾讯/澎湃 RSS entries=0 的真实原因 + 找最后一批能跑的"""
import httpx, feedparser, re

UA = {"User-Agent": "Mozilla/5.0"}

# 腾讯新闻 RSS
for name, url in [
    ("腾讯新闻-食品", "https://news.qq.com/rss/channel/food.xml"),
    ("腾讯新闻首页", "https://news.qq.com/rss/index.xml"),
    ("腾讯新闻-财经", "https://news.qq.com/rss/channel/finance.xml"),
    ("澎湃新闻", "https://www.thepaper.cn/rss.xml"),
    ("澎湃-消费", "https://www.thepaper.cn/channel_25951.xml"),
    ("新华网-食品", "http://www.news.cn/food/rss.xml"),
    ("人民网-食品", "http://www.people.com.cn/rss/food.xml"),
]:
    try:
        r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        print(f"\n=== {name} ===")
        print(f"  status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 500:
            # 看原始 XML 结构
            print(f"  原文前500字:")
            print(f"  {r.text[:500]}")
            # 手动正则找 item
            items = re.findall(r"<item[^>]*>", r.text)
            print(f"  <item> 标签数: {len(items)}")
            entries = re.findall(r"<entry[^>]*>", r.text)
            print(f"  <entry> 标签数: {len(entries)}")
            # feedparser
            feed = feedparser.parse(r.text)
            print(f"  feedparser entries: {len(feed.entries)}")
    except Exception as e:
        print(f"\n=== {name} ===  {str(e)[:50]}")

# 再试几个可能有 RSS 但 URL 不对的
print("\n\n=== 额外测试 ===")
extra = [
    ("新华网首页RSS", "http://www.news.cn/rss.xml"),
    ("人民网首页RSS", "http://www.people.com.cn/rss/politics.xml"),
    ("新浪财经RSS", "https://finance.sina.com.cn/roll/index.d.html?cid=56592"),  # 不是 RSS 是列表
    ("搜狐食品频道", "https://food.sohu.com/"),  # 静态
    ("中国食品工业网-备用", "http://www.cfia.net/xwzx/"),
]
for name, url in extra:
    try:
        r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        print(f"  {name}: {r.status_code} len={len(r.text)}")
    except Exception as e:
        print(f"  {name}: {str(e)[:40]}")