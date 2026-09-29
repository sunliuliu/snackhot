"""修复能爬的零售站的编码 + 再加一批真实能通的"""
import httpx, time
from bs4 import BeautifulSoup
import io

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}
WIDE_FOOD = ["食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙",
             "辣条","魔芋","奥利奥","烘焙","饼干","糖巧","肉脯","卤味","洽洽",
             "旺旺","绝味","盐津铺子","来伊份","好想来","零食很忙","赵一鸣",
             "休闲食品","食品工业","食品饮料","快消","便利店","量贩","零售",
             "门店","加盟","连锁","供应链","渠道","营销","消费","品牌"]

# ==============================================
# 1. 联商网 —— 修编码（GB2312/GBK）
# ==============================================
print("="*70)
print("1. 联商网 linkshop.com - 修编码")
print("="*70)
r = httpx.get("http://www.linkshop.com/", headers=UA, timeout=10, verify=False)
# 先看原始 content-type
print(f"  content-type: {r.headers.get('content-type', 'N/A')}")
print(f"  encoding 自动检测: {r.encoding}  apparent_encoding: {r.apparent_encoding}")

# 手动强制 GBK 解码
raw = r.content
for enc in ["gbk", "gb2312", "gb18030", "utf-8"]:
    try:
        decoded = raw.decode(enc)
        # 检测有没有中文（看前 2000 字）
        has_cn = any('\u4e00' <= c <= '\u9fff' for c in decoded[:2000])
        print(f"  {enc}: OK  has_chinese={has_cn}")
        if has_cn:
            r.text = decoded  # 替换
            break
    except Exception as e:
        print(f"  {enc}: FAIL {str(e)[:40]}")

soup = BeautifulSoup(r.text, "lxml")
arts = []
for a in soup.find_all("a", href=True):
    txt = a.get_text(strip=True)
    href = a.get("href", "")
    if len(txt) < 15: continue
    if ".shtml" in href or "/news/" in href:
        if href.startswith("//"): href = "https:" + href
        elif href.startswith("/"): href = "http://www.linkshop.com" + href
        arts.append((txt, href))
seen = set(); uniq = []
for t, h in arts:
    if h not in seen and h.startswith("http"):
        seen.add(h); uniq.append((t, h))
snack = [(t,h) for t,h in uniq if any(k in t for k in WIDE_FOOD)]
print(f"\n  ✅ 修复后: 总文章 {len(uniq)}, 食品/零售相关 {len(snack)}")
for t, h in snack[:10]:
    print(f"    ✅ {t[:55]}")
    print(f"       {h[:70]}")

# 如果首页没零食，看看有没有频道入口
print("\n  频道入口探测：")
channel_hints = []
for a in soup.find_all("a", href=True):
    txt = a.get_text(strip=True)
    href = a.get("href", "")
    if len(txt) < 4: continue
    if any(k in txt for k in ["食品","零售","快消","便利店","超市","零食","餐饮"]):
        channel_hints.append((txt, href))
for t, h in channel_hints[:15]:
    print(f"     {t[:15]} -> {h[:50]}")

# ==============================================
# 2. 中国糖果网 + 中国休闲食品网 —— 爬零食相关
# ==============================================
print("\n" + "="*70)
print("2. 中国糖果网 + 休闲食品网")
print("="*70)
for name, base_url in [
    ("中国糖果网", "http://www.candy001.com"),
    ("中国休闲食品网", "http://www.xxspw.com"),
]:
    r = httpx.get(base_url + "/", headers=UA, timeout=8, verify=False)
    if r.status_code != 200:
        print(f"  {name}: HTTP {r.status_code}")
        continue
    # 试编码
    for enc in [r.apparent_encoding, "gbk", "gb2312", "utf-8"]:
        if enc:
            try:
                decoded = r.content.decode(enc)
                if any('\u4e00' <= c <= '\u9fff' for c in decoded[:2000]):
                    r.text = decoded
                    break
            except: pass
    soup = BeautifulSoup(r.text, "lxml")
    arts = []
    for a in soup.find_all("a", href=True):
        txt = a.get_text(strip=True)
        href = a.get("href", "")
        if len(txt) < 15: continue
        if not href.startswith("http"):
            if href.startswith("//"): href = "http:" + href
            elif href.startswith("/"): href = base_url + href
            else: continue
        if any(k in txt for k in WIDE_FOOD):
            arts.append((txt, href))
    print(f"  {name}: 找到 {len(arts)} 条零食/食品相关")
    for t, h in arts[:5]:
        print(f"    ✅ {t[:50]}")
        print(f"       {h[:70]}")
    time.sleep(0.3)

# ==============================================
# 3. 微信公众号 RSS —— 通过第三方聚合
# ==============================================
print("\n" + "="*70)
print("3. 微信公众号 RSS (第三方聚合)")
print("="*70)
wechat_rss = [
    ("食品板 RSSHub", "https://rsshub.app/wechat/mp/msgalbum/2147573872/album_2147573872"),
    ("零食行业公众号", "https://rsshub.app/wechat/search?keyword=零食行业"),
    ("Foodaily", "https://rsshub.app/foodaily/feed"),
    ("新榜食品榜", "https://rsshub.app/newrank/channel/49"),
    ("好想来", "https://rsshub.app/wechat/mp/home/TXJcMzIyMjg2OA"),
]
for name, url in wechat_rss:
    try:
        r = httpx.get(url, headers=UA, timeout=10)
        import feedparser
        feed = feedparser.parse(r.text)
        n = len(feed.entries)
        titles = [e.get("title","") for e in feed.entries]
        print(f"  {name}: {n} 条, status={r.status_code}")
        for t in titles[:3]:
            print(f"    - {t[:50]}")
    except Exception as e:
        print(f"  {name}: ERR {str(e)[:50]}")
    time.sleep(0.3)

# ==============================================
# 4. 抖音本地生活团购 + 美团闪购（试试 RSSHub）
# ==============================================
print("\n" + "="*70)
print("4. RSSHub 零食/零售相关")
print("="*70)
rsshub_tests = [
    ("抖音用户", "https://rsshub.app/douyin/user/7266790026400262427"),  # 好想来
    ("微博零食话题", "https://rsshub.app/weibo/search/%E9%9B%B6%E9%A3%9F"),
    ("知乎零食话题", "https://rsshub.app/zhihu/topic/19554987"),
    ("小红书零食测评", "https://rsshub.app/xiaohongshu/user/5d657e000000000009012345"),
    ("B站零食测评", "https://rsshub.app/bilibili/channel/2117883"),  # 食品
]
for name, url in rsshub_tests:
    try:
        r = httpx.get(url, headers=UA, timeout=10)
        import feedparser
        feed = feedparser.parse(r.text)
        n = len(feed.entries)
        print(f"  {name}: feed={feed.version}, entries={n}, status={r.status_code}")
        if n > 0:
            for e in feed.entries[:2]:
                print(f"    - {e.get('title','')[:50]}")
    except Exception as e:
        print(f"  {name}: ERR {str(e)[:50]}")
    time.sleep(0.3)