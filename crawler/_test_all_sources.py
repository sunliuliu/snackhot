"""并行测试所有候选信源，找能通的 URL + 结构"""
import httpx, feedparser, time, re
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36"}

# ====================================================
# 1. RSS 信源（最稳定）
# ====================================================
rss_candidates = [
    ("亿邦动力 - 食品频道", "https://www.ebrun.com/rss/food.xml"),
    ("36氪 - 食品餐饮",    "https://36kr.com/feed/column/49"),
    ("36氪 - 全站",        "https://36kr.com/feed"),
    ("澎湃新闻 - 消费",    "https://www.thepaper.cn/channel_25951"),   # 可能不是 RSS
    ("第一财经 - 消费",    "https://www.yicai.com/rss/consume.xml"),
    ("界面新闻 - 消费",    "https://www.jiemian.com/rss/consume.xml"),
    ("知乎热榜",           "https://www.zhihu.com/rss"),
    ("搜狐 - 食品频道",    "https://rss.sohu.com/ch_index_44.xml"),
    ("中国食品工业网",      "http://www.cfia.net/rss.xml"),
    ("食品伙伴网 - 资讯",   "https://www.foodmate.net/rss/news.xml"),
    ("豆果美食 - 行业",     "https://www.douguo.com/rss/industry.xml"),
    ("亿邦动力 - 新零售",  "https://www.ebrun.com/rss/retail.xml"),
]
print("="*60)
print("RSS 信源测试")
print("="*60)
for name, url in rss_candidates:
    try:
        r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        if r.status_code == 200 and len(r.text) > 500:
            feed = feedparser.parse(r.text)
            n = len(feed.entries)
            if n > 0:
                title = feed.entries[0].get("title","")[:50]
                print(f"[OK] {name:20s} {url[:60]:60s} entries={n:>4}  首条: {title}")
            else:
                print(f"[OK] {name:20s} {url[:60]:60s} entries=0  (feed 格式对但无条目)")
        else:
            print(f"[FAIL] {name:20s} {url[:60]:60s} HTTP {r.status_code}")
    except Exception as e:
        print(f"[ERR] {name:20s} {url[:60]:60s} {str(e)[:40]}")

# ====================================================
# 2. 网页信源
# ====================================================
print("\n" + "="*60)
print("网页信源测试")
print("="*60)

sites = [
    ("巨潮资讯 - 零食公司全量公告", "http://www.cninfo.com.cn/new/hisAnnouncement/query", 
     {"pageSize":50,"pageNum":1,"seDate":"2026-09-25~2026-09-29","tabName":"fulltext","column":"szse","category":"","plate":""}),
    ("东方财富 - 财经要闻", "https://finance.eastmoney.com/a/czqyw.html", None),
    ("东方财富 - 公司频道", "https://finance.eastmoney.com/a/cgsxw.html", None),
    ("东方财富 - 滚动新闻", "https://finance.eastmoney.com/a/ccjxw.html", None),
    ("东方财富 - 食品饮料板块研究", "https://data.eastmoney.com/report/shyjslist.html?industryCode=478000", None),
    ("Foodaily 资讯列表", "https://www.foodaily.com/index.php/articles", None),
    ("界面新闻 - 消费", "https://www.jiemian.com/lists/84.html", None),
    ("澎湃新闻 - 消费", "https://www.thepaper.cn/channel_25951", None),
]
for name, url, data in sites:
    try:
        if data is not None:
            # POST
            r = httpx.post(url, data=data, headers={**UA, "Origin":"http://www.cninfo.com.cn", "Referer":"http://www.cninfo.com.cn/"}, timeout=10, follow_redirects=True)
        else:
            r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        if r.status_code == 200:
            if "cninfo" in url:
                d = r.json()
                anns = d.get("announcements") or []
                # 找零食相关
                snack_anns = [a for a in anns if any(kw in (a.get("secName","") + a.get("announcementTitle","")) for kw in ["食品","坚果","零食","糖果","卫龙","三只松鼠","良品","盐津","绝味","洽洽","来伊份","旺旺"])]
                print(f"[OK] {name}  全量{len(anns)}条, 零食相关={len(snack_anns)}条")
                for a in snack_anns[:3]:
                    print(f"      - [{a.get('secName')}] {a.get('announcementTitle','')[:60]}")
            else:
                # 网页：统计 a 标签 + 零食关键词
                soup = BeautifulSoup(r.text, "lxml")
                all_a = soup.find_all("a", href=True)
                snack_links = [a for a in all_a if any(kw in a.get_text() for kw in ["零食","坚果","卫龙","三只松鼠","良品","糖果","辣条","魔芋","奥利奥","洽洽"])]
                print(f"[OK] {name:28s} HTTP 200, links={len(all_a)}, 零食相关={len(snack_links)}")
                for a in snack_links[:3]:
                    print(f"      - {a.get('href','')[:70]} | {a.get_text(strip=True)[:50]}")
        else:
            print(f"[FAIL] {name:28s} HTTP {r.status_code}")
    except Exception as e:
        print(f"[ERR] {name:28s} {str(e)[:50]}")