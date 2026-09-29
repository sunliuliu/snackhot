import httpx, json, re
from datetime import datetime, timedelta

def t1_cninfo():
    print("=== 巨潮资讯 ===")
    today = datetime.now()
    sd = (today - timedelta(days=3)).strftime("%Y-%m-%d")
    ed = today.strftime("%Y-%m-%d")
    payload = {
        "pageSize": 30, "pageNum": 1,
        "seDate": f"{sd}~{ed}",
        "tabName": "fulltext", "column": "szse",
        "category": "", "plate": "",
    }
    r = httpx.post("http://www.cninfo.com.cn/new/hisAnnouncement/query", 
        data=payload, timeout=15,
        headers={"User-Agent":"SnackHot","Origin":"http://www.cninfo.com.cn","Referer":"http://www.cninfo.com.cn/"}
    )
    d = r.json()
    print(f"  total={d.get('totalAnnouncement')}, announcements={len(d.get('announcements') or [])}")
    anns = d.get("announcements") or []
    for a in anns[:5]:
        title = a.get("announcementTitle","").replace("<em>","").replace("</em>","")[:80]
        print(f"  - [{a.get('secName')}] {title}")

def t2_eastmoney():
    print("\n=== 东方财富 ===")
    # 找新 URL
    candidates = [
        "https://finance.eastmoney.com/a/czqyw.html",
        "https://finance.eastmoney.com/a/csyyw.html", 
        "https://finance.eastmoney.com/a/cgpp.html",
        "https://finance.eastmoney.com/a/cfbc.html",
        "https://finance.eastmoney.com/a/cchb.html",
    ]
    for u in candidates:
        try:
            r = httpx.get(u, timeout=10, follow_redirects=True, headers={"User-Agent":"Mozilla/5.0"})
            print(f"  {r.status_code} {u}")
        except Exception as e:
            print(f"  ERR {u} {e}")
    # 首页看结构
    try:
        r = httpx.get("https://finance.eastmoney.com/", timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        links = sorted(set(re.findall(r'href="(/a/[^"]+)"', r.text)))[:15]
        print(f"  homepage /a/ links: {links}")
    except Exception as e:
        print(f"  homepage ERR: {e}")

def t3_foodaily():
    print("\n=== Foodaily ===")
    r = httpx.get("https://www.foodaily.com/index.php/newsflashes", timeout=15,
        headers={"User-Agent":"Mozilla/5.0"})
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "lxml")
    # 找所有 a 标签
    links = soup.select("a[href]")
    print(f"  total links: {len(links)}")
    food_links = [a for a in links if "foodaily" in a.get("href","").lower() or "/articles/" in a.get("href","").lower() or "/newsflashes/" in a.get("href","").lower()]
    print(f"  food-related links: {len(food_links)}")
    for a in food_links[:5]:
        print(f"    - {a.get('href')[:80]} | {a.get_text(strip=True)[:50]}")

t1_cninfo()
t2_eastmoney()
t3_foodaily()