"""深挖几个看起来好但没拿到条目的站"""
import httpx, feedparser

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}

# 1. 36氪 feed —— entries=0 可能是 header 问题
print("=== 36氪 ===")
for url in ["https://36kr.com/feed", "https://36kr.com/feed/column/49", "https://36kr.com/feed/newsflash"]:
    try:
        r = httpx.get(url, headers={**UA, "Accept": "application/rss+xml, application/xml, text/xml"}, timeout=10)
        feed = feedparser.parse(r.text)
        print(f"  {url}")
        print(f"    status={r.status_code} feed-version={feed.version} entries={len(feed.entries)}")
        if feed.entries:
            print(f"    first title: {feed.entries[0].get('title','')[:60]}")
    except Exception as e:
        print(f"  {url} -> {e}")

# 2. 澎湃 RSS
print("\n=== 澎湃 ===")
for url in ["https://www.thepaper.cn/rss.xml", "https://www.thepaper.cn/channel_25951.xml"]:
    try:
        r = httpx.get(url, headers=UA, timeout=10)
        feed = feedparser.parse(r.text)
        print(f"  {url}")
        print(f"    status={r.status_code} feed-version={feed.version} entries={len(feed.entries)}")
        if feed.entries:
            print(f"    first: {feed.entries[0].get('title','')[:60]}")
    except Exception as e:
        print(f"  {url} -> {e}")

# 3. 腾讯新闻 - 食品 RSS
print("\n=== 腾讯新闻 ===")
for url in ["https://news.qq.com/rss/", "https://new.qq.com/ch/food/", "https://www.163.com/rss/news.xml"]:
    try:
        r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        print(f"  {url} -> {r.status_code} final={str(r.url)[:60]} len={len(r.text)}")
    except Exception as e:
        print(f"  {url} -> {e}")

# 4. 更宽泛的关键词过滤测试（东方财富/界面/澎湃 加"食品饮料"也过滤）
print("\n=== 东方财富 用更宽泛关键词 ===")
r = httpx.get("https://finance.eastmoney.com/a/cyyzsp.html", headers=UA, timeout=10, follow_redirects=True)
from bs4 import BeautifulSoup
soup = BeautifulSoup(r.text, "lxml")
all_a = soup.find_all("a", href=True)
wide_kw = ["食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙","辣条","魔芋","奥利奥","烘焙","糕点","饼干","糖巧","肉脯","卤味"]
matched = [a for a in all_a if any(kw in a.get_text() for kw in wide_kw) and len(a.get_text()) > 8]
print(f"  links={len(all_a)}, 宽泛食品匹配={len(matched)}")
for a in matched[:5]:
    print(f"    - {a.get_text(strip=True)[:60]}")

# 5. Foodaily 分类页
print("\n=== Foodaily 分类页 ===")
for cid, name in [("7","零食"),("13","糖果巧克力"),("9","饼干糕点"),("11","肉脯卤味"),("10","坚果炒货"),("8","膨化食品")]:
    url = f"https://www.foodaily.com/index.php/articles?catId={cid}"
    try:
        r = httpx.get(url, headers=UA, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        links = soup.find_all("a", href=True)
        art_links = [a for a in links if "/articles/" in a.get("href","")]
        titles = list(set(a.get_text(strip=True) for a in art_links if len(a.get_text()) > 10))
        print(f"  catId={cid}({name}): {len(titles)} 条文章")
        for t in titles[:3]:
            print(f"    - {t[:60]}")
    except Exception as e:
        print(f"  catId={cid}({name}): {e}")