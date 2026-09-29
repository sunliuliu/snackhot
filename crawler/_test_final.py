"""测试新浪财经 + 搜狐财经 + 巨潮 secid 精确"""
import httpx
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}
kw = ["食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙",
      "辣条","魔芋","奥利奥","烘焙","糕点","饼干","糖巧","肉脯","卤味",
      "洽洽","旺旺","绝味","盐津铺子","来伊份"]

# A. 巨潮：精确 secid 列表（之前能跑通，现在拉 3 天数据看有几个公司有公告）
print("=== 巨潮 零食 7 家精确 ===")
stocks = [
    ("300783", "三只松鼠"), ("603716", "良品铺子"), ("603517", "绝味食品"),
    ("002847", "盐津铺子"), ("002557", "洽洽食品"), ("603887", "来伊份"),
    ("002495", "佳隆股份"),  # 调味品 → 食品饮料
    ("600872", "中炬高新"),  # 厨邦酱油
]
import json
any_hit = False
for code, name in stocks:
    try:
        r = httpx.post("http://www.cninfo.com.cn/new/hisAnnouncement/query", data={
            "stock": f"{name},{code}",
            "tabName": "fulltext", "pageSize": "5", "pageNum": "1",
            "seDate": "2026-09-25~2026-09-29",
            "column": "szse" if code.startswith("0") or code.startswith("3") else "sse",
            "category": "",
        }, headers={**UA, "Origin": "http://www.cninfo.com.cn", "Referer": "http://www.cninfo.com.cn/"}, timeout=10)
        d = r.json()
        anns = d.get("announcements") or []
        if anns:
            any_hit = True
            print(f"  [{name}({code})] {len(anns)} 条公告:")
            for a in anns[:3]:
                t = a.get("announcementTitle","").replace("<em>","").replace("</em>","")[:60]
                print(f"    - {t}")
        else:
            print(f"  [{name}({code})] 无公告")
    except Exception as e:
        print(f"  [{name}({code})] ERR {str(e)[:40]}")
print(f"  有公告的公司: {any_hit}")

# B. 新浪财经 食品
print("\n=== 新浪财经 ===")
for url in [
    "https://finance.sina.com.cn/food/",
    "https://finance.sina.com.cn/roll/",  # 滚动新闻
    "https://www.sina.com.cn/",
]:
    try:
        r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        soup = BeautifulSoup(r.text, "lxml")
        links = soup.find_all("a", href=True)
        matched = [(a.get_text(strip=True), a.get("href","")) for a in links 
                   if any(k in a.get_text() for k in kw) and len(a.get_text()) > 10]
        print(f"  {url.split('//')[1].split('/')[0]} ({url[-15:]}): {len(matched)} 条食品相关")
        for t, h in matched[:3]:
            print(f"    {h[:70]} | {t[:50]}")
    except Exception as e:
        print(f"  {url[:50]}: ERR {str(e)[:40]}")

# C. 搜狐财经 食品
print("\n=== 搜狐财经 ===")
for url in ["https://food.sohu.com/", "https://www.sohu.com/category/food/"]:
    try:
        r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        soup = BeautifulSoup(r.text, "lxml")
        links = soup.find_all("a", href=True)
        matched = [(a.get_text(strip=True), a.get("href","")) for a in links 
                   if len(a.get_text()) > 10 and ("sohu.com/a/" in a.get("href","") or "/a/" in a.get("href",""))]
        print(f"  {url}: {len(matched)} 文章链接")
        for t, h in matched[:5]:
            hit = "✅" if any(k in t for k in kw) else ""
            print(f"    {hit} {h[:60]} | {t[:45]}")
    except Exception as e:
        print(f"  {url}: ERR {str(e)[:40]}")

# D. 每日经济新闻 食品
print("\n=== 每日经济新闻 ===")
r = httpx.get("https://www.nbd.com.cn/columns/596", headers=UA, timeout=10)
print(f"  status={r.status_code} len={len(r.text)}")
soup = BeautifulSoup(r.text, "lxml")
links = soup.find_all("a", href=True)
for a in links[:30]:
    if "articles" in a.get("href","") or "/articles/" in a.get("href",""):
        t = a.get_text(strip=True)
        if len(t) > 15:
            print(f"    {a.get('href','')[:60]} | {t[:45]}")