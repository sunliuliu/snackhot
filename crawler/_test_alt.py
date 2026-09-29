"""测国内可用的 RSS/微信聚合替代方案"""
import httpx, feedparser, time

UA = {"User-Agent": "Mozilla/5.0"}
WIDE_KW = ["食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙",
           "辣条","魔芋","奥利奥","烘焙","饼干","糖巧","肉脯","卤味","洽洽",
           "旺旺","绝味","盐津铺子","来伊份","好想来","零食很忙","赵一鸣",
           "休闲食品","食品工业","食品饮料","快消","便利店","量贩","零售",
           "门店","加盟","连锁","供应链","渠道","营销","消费","品牌"]

# ===== A. RSSHub 国内备用实例（GitHub 上有人维护的）=====
print("="*70)
print("A. RSSHub 国内备用实例")
print("="*70)
backup_hubs = [
    ("rsshub.feeded.com", "https://rsshub.feeded.com"),
    ("rsshub.rssforever.com", "https://rsshub.rssforever.com"),
    ("rsshub.pseudoyu.com", "https://rsshub.pseudoyu.com"),
    ("rsshub.uneasy.win", "https://rsshub.uneasy.win"),
    ("rsshub.kekylin.com", "https://rsshub.kekylin.com"),
    ("rsshub.lskyf.com", "https://rsshub.lskyf.com"),
    ("rsshub.copl.dev", "https://rsshub.copl.dev"),
    ("rsshub.6661.xyz", "https://rsshub.6661.xyz"),
    ("rsshub.helloworld.pw", "https://rsshub.helloworld.pw"),
]
test_path = "/wechat/mp/search?keyword=零食行业&limit=3"
for name, hub in backup_hubs:
    try:
        r = httpx.get(f"{hub}{test_path}", headers=UA, timeout=10)
        if r.status_code == 200 and len(r.text) > 300:
            feed = feedparser.parse(r.text)
            n = len(feed.entries)
            titles = [e.get("title","") for e in feed.entries]
            snack_n = sum(1 for t in titles if any(k in t for k in WIDE_KW))
            print(f"  ✅ {name:30s} v={feed.version} {n}条 snack={snack_n} ({len(r.text)}b)")
            for t in titles[:2]:
                print(f"      - {t[:50]}")
        elif r.status_code in (301, 302):
            print(f"  ➡️  {name:30s} redirect {r.headers.get('location','')[:50]}")
        else:
            print(f"  ❌ {name:30s} HTTP {r.status_code}")
    except Exception as e:
        print(f"  ❌ {name:30s} {str(e)[:40]}")

# ===== B. 直接测微信公众号专用 RSS 服务 =====
print("\n" + "="*70)
print("B. 微信公众号 RSS 专用服务")
print("="*70)
wechat_services = [
    ("feedx.net 搜索", "https://feedx.net/search?q=零食行业"),
    ("feedx.net 主页", "https://feedx.net/"),
    ("ezrss.io", "https://ezrss.io/"),
    ("rsshub 自建建议", "需要自行部署 RSSHub"),
    ("we2rss 微信", "https://we2rss.cn/"),
    ("feedly.io", "https://feedly.io/"),
]
for name, url in wechat_services:
    try:
        r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        print(f"  {name:20s} -> HTTP {r.status_code} ({len(r.text)}b)  final={str(r.url)[:50]}")
    except Exception as e:
        print(f"  {name:20s} -> {str(e)[:50]}")

# ===== C. 找几个能直接抓的食品/快消 RSS =====
print("\n" + "="*70)
print("C. 真实食品/快消类 RSS Feed（非 RSSHub）")
print("="*70)
real_rss = [
    ("Foodaily 食品饮料", "https://www.foodaily.com/rss.xml"),
    ("Foodaily 行业资讯", "https://www.foodaily.com/index.php/rss.xml"),
    ("亿邦动力", "https://www.ebrun.com/rss.xml"),
    ("亿邦动力-新零售", "https://www.ebrun.com/retail/rss.xml"),
    ("第一财经", "https://www.yicai.com/rss/"),
    ("界面新闻", "https://www.jiemian.com/rss.xml"),
    ("澎湃新闻", "https://www.thepaper.cn/rss.xml"),
    ("每日经济新闻", "https://www.nbd.com.cn/rss.xml"),
    ("中国网-食品", "http://www.china.com.cn/rss/food.xml"),
    ("新华网-食品", "http://www.news.cn/rss/food.xml"),
    ("网易新闻-食品", "https://news.163.com/special/0001386F/rss.xml"),
    ("腾讯新闻-食品", "https://news.qq.com/rss/channel/food.xml"),
]
for name, url in real_rss:
    try:
        r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        if r.status_code == 200 and len(r.text) > 300:
            feed = feedparser.parse(r.text)
            n = len(feed.entries)
            if n > 0:
                titles = [e.get("title","") for e in feed.entries]
                snack_n = sum(1 for t in titles if any(k in t for k in WIDE_KW))
                print(f"  ✅ {name:20s} {n}条 snack={snack_n}")
                for t in titles[:2]:
                    print(f"      - {t[:50]}")
            else:
                print(f"  ⚠️  {name:20s} feed 但无条目 (v={feed.version})")
        elif r.status_code == 404:
            print(f"  ❌ {name:20s} 404")
        else:
            print(f"  ❌ {name:20s} HTTP {r.status_code}")
    except Exception as e:
        print(f"  ❌ {name:20s} {str(e)[:40]}")
    time.sleep(0.3)