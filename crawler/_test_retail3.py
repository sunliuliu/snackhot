"""修正策略：联商网换 domain + 新榜零食号 + 食品伙伴网 RSS + 微信公众号搜狗"""
import httpx, feedparser, time
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}
WIDE_FOOD = ["食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙",
             "辣条","魔芋","奥利奥","烘焙","饼干","糖巧","肉脯","卤味","洽洽",
             "旺旺","绝味","盐津铺子","来伊份","好想来","零食很忙","赵一鸣",
             "休闲食品","食品工业","食品饮料","快消","便利店","量贩","零售"]

# ==============================================
# 1. 联商网 —— 改用新域名 linkshop.com（无 SSL 问题）
# ==============================================
print("="*70)
print("1. 联商网 linkshop.com（新域名）")
print("="*70)
r = httpx.get("https://www.linkshop.com/", headers=UA, timeout=10, follow_redirects=True, verify=False)
print(f"  status={r.status_code} final={str(r.url)[:60]} len={len(r.text)}")
if r.status_code == 200:
    soup = BeautifulSoup(r.text, "lxml")
    # 找所有 .shtml 结尾的文章链接
    arts = []
    for a in soup.find_all("a", href=True):
        txt = a.get_text(strip=True)
        href = a.get("href", "")
        if len(txt) < 15: continue
        if ".shtml" in href or "/news/" in href:
            if href.startswith("//"): href = "https:" + href
            elif href.startswith("/"): href = "https://www.linkshop.com" + href
            arts.append((txt, href))
    seen = set(); uniq = []
    for t, h in arts:
        if h not in seen and h.startswith("http"):
            seen.add(h); uniq.append((t, h))
    snack = [(t,h) for t,h in uniq if any(k in t for k in WIDE_FOOD)]
    print(f"  总文章 {len(uniq)}, 食品/零食/零售相关 {len(snack)}")
    for t, h in snack[:10]:
        print(f"    ✅ {t[:55]}")
        print(f"       {h[:70]}")
    if not snack and uniq:
        print("  宽泛看前10条：")
        for t, h in uniq[:10]:
            print(f"     {t[:50]}  <- {h[-30:]}")

# 联商网食品专栏
for url in ["https://www.linkshop.com/food/", "https://www.linkshop.com/news/food/", "https://www.linkshop.com/column/syjs/"]:
    try:
        r = httpx.get(url, headers=UA, timeout=8, verify=False)
        if r.status_code == 200 and len(r.text) > 3000:
            print(f"  ✅ {url} ({len(r.text)} bytes)")
        elif r.status_code == 404:
            print(f"  ❌ {url} -> 404")
        else:
            print(f"  ⚠️  {url} -> {r.status_code}")
    except Exception as e:
        print(f"  ❌ {url} -> {str(e)[:40]}")

# ==============================================
# 2. 食品伙伴网 RSS
# ==============================================
print("\n" + "="*70)
print("2. 食品伙伴网 + 其他 RSS")
print("="*70)
rss_urls = [
    ("食品伙伴网 资讯", "https://www.foodmate.net/rss/news.xml"),
    ("食品伙伴网 行业", "https://www.foodmate.net/rss/industry.xml"),
    ("食品伙伴网 原料", "https://www.foodmate.net/rss/material.xml"),
    ("中国食品工业网", "http://www.cfia.net/rss.xml"),
    ("中国酒业新闻网", "https://www.cnwinenews.com/rss.xml"),
    ("中国调味品协会", "https://www.condiment.org/rss.xml"),
]
for name, url in rss_urls:
    try:
        r = httpx.get(url, headers=UA, timeout=8, follow_redirects=True)
        if r.status_code == 200 and len(r.text) > 500:
            feed = feedparser.parse(r.text)
            n = len(feed.entries)
            titles = [e.get("title","") for e in feed.entries]
            snack_n = sum(1 for t in titles if any(k in t for k in WIDE_FOOD))
            if n > 0:
                print(f"  ✅ {name}: {n} 条, 食品/零食相关 {snack_n}")
                for e in feed.entries[:3]:
                    print(f"      - {e.get('title','')[:60]}")
            else:
                print(f"  ⚠️  {name}: feed 但无条目")
        else:
            print(f"  ❌ {name}: HTTP {r.status_code} len={len(r.text)}")
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:40]}")
    time.sleep(0.3)

# ==============================================
# 3. 微信公众号搜狗（零食行业大号）
# ==============================================
print("\n" + "="*70)
print("3. 微信公众号搜狗（零食行业号）")
print("="*70)
wechat_sites = [
    ("搜狗微信搜索 - 零食", "https://weixin.sogou.com/weixin?type=2&query=零食行业"),
    ("搜狗微信搜索 - 三只松鼠", "https://weixin.sogou.com/weixin?type=2&query=三只松鼠+最新消息"),
    ("新榜 - 食品行业榜", "https://www.newrank.cn/rank/industry?industry=食品饮料&range=1"),
]
for name, url in wechat_sites:
    try:
        r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        print(f"  {name}: status={r.status_code} len={len(r.text)}")
        if r.status_code == 200 and len(r.text) > 2000:
            soup = BeautifulSoup(r.text, "lxml")
            arts = []
            for a in soup.find_all("a", href=True):
                txt = a.get_text(strip=True)
                href = a.get("href", "")
                if len(txt) > 15 and ("sogou" in href or "mp.weixin" in href):
                    arts.append((txt, href))
            print(f"    文章链接: {len(arts)}")
            for t, h in arts[:3]:
                print(f"      - {t[:50]}")
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:50]}")
    time.sleep(0.5)

# ==============================================
# 4. 再试几个可能有料的零食专门站
# ==============================================
print("\n" + "="*70)
print("4. 零食专门站 + 行业站")
print("="*70)
special = [
    ("零食在线", "http://www.ling-shi.com.cn/"),
    ("零食网", "http://www.0733food.com/"),
    ("食品行业网", "http://www.foodonline.com.cn/"),
    ("中国休闲食品网", "http://www.xxspw.com/"),
    ("烘焙在线", "http://www.hbzxw.com/"),
    ("中国糖果网", "http://www.candy001.com/"),
    ("食品商务网", "https://www.21food.cn/"),
    ("慧聪食品网", "http://food.hc360.com/"),
]
for name, url in special:
    try:
        r = httpx.get(url, headers=UA, timeout=8, follow_redirects=True, verify=False)
        if r.status_code == 200 and len(r.text) > 3000:
            soup = BeautifulSoup(r.text, "lxml")
            arts = []
            for a in soup.find_all("a", href=True):
                txt = a.get_text(strip=True)
                if len(txt) > 15 and any(k in txt for k in WIDE_FOOD):
                    arts.append((txt, a.get("href","")))
            print(f"  ✅ {name}: {len(r.text)} bytes, 食品相关 {len(arts)}")
            for t, h in arts[:3]:
                print(f"      - {t[:50]}")
        else:
            print(f"  ❌ {name}: HTTP {r.status_code} len={len(r.text)}")
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:40]}")
    time.sleep(0.3)