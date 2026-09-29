"""测试更多能静态爬的网页信源"""
import httpx, json
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}

wide_kw = ["食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙",
           "辣条","魔芋","奥利奥","烘焙","糕点","饼干","糖巧","肉脯","卤味",
           "米","面","乳品","快消","消费","零售","量贩"]

# A. 东方财富 —— 找它的滚动新闻 API
print("=== 东方财富 API ===")
apis = [
    ("滚动新闻", "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns?client=web&biz=web_news_col&column=350&order=1&needInteractData=0&page_index=1&page_size=30"),
    ("财经早知道", "https://finance.eastmoney.com/a/cyyzsp.html"),  # 直接爬列表
    ("食品饮料行业快讯", "https://data.eastmoney.com/notices/syjs.html"),
    ("公告 - 行业", "https://np-anotice-stock.eastmoney.com/api/security/ann?page_size=30&page_index=1&ann_type=SHA&client_source=web&f_node=0&s_node=48"),
]
for name, url in apis:
    try:
        r = httpx.get(url, headers={**UA, "Referer": "https://finance.eastmoney.com/"}, timeout=10)
        print(f"  {name}: status={r.status_code} len={len(r.text)} content-type={r.headers.get('content-type','')[:30]}")
        if "json" in r.headers.get("content-type",""):
            d = r.json()
            print(f"    keys: {list(d.keys())[:6]}")
    except Exception as e:
        print(f"  {name}: ERR {str(e)[:60]}")

# B. 腾讯新闻食品
print("\n=== 腾讯新闻食品 ===")
r = httpx.get("https://news.qq.com/ch/food/", headers=UA, timeout=10)
soup = BeautifulSoup(r.text, "lxml")
links = soup.find_all("a", href=True)
for a in links[:20]:
    txt = a.get_text(strip=True)
    if len(txt) > 10:
        print(f"  {a.get('href','')[:80]} | {txt[:50]}")

# C. 澎湃新闻 消费
print("\n=== 澎湃新闻 消费 ===")
r = httpx.get("https://www.thepaper.cn/channel_25951", headers=UA, timeout=10)
soup = BeautifulSoup(r.text, "lxml")
links = soup.find_all("a", href=True)
matched = [a for a in links if len(a.get_text()) > 15]
print(f"  长文本链接: {len(matched)}")
for a in matched[:10]:
    txt = a.get_text(strip=True)
    href = a.get("href","")
    if "/newsDetail_" in href or "/detail_" in href:
        print(f"  {href[:80]} | {txt[:50]}")

# D. 界面新闻 消费
print("\n=== 界面新闻 消费 ===")
r = httpx.get("https://www.jiemian.com/lists/84.html", headers=UA, timeout=10, follow_redirects=True)
soup = BeautifulSoup(r.text, "lxml")
links = soup.find_all("a", href=True)
matched = [a for a in links if len(a.get_text()) > 15]
print(f"  长文本链接: {len(matched)}")
for a in matched[:15]:
    txt = a.get_text(strip=True)
    href = a.get("href","")
    if "/article/" in href or href.endswith(".html"):
        print(f"  {href[:80]} | {txt[:50]}")

# E. 亿邦动力 首页 + 新零售
print("\n=== 亿邦动力 ===")
for url in ["https://www.ebrun.com/", "https://www.ebrun.com/retail/"]:
    r = httpx.get(url, headers=UA, timeout=10)
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("a", href=True)
    matched = [(a.get_text(strip=True), a.get("href","")) for a in links if len(a.get_text()) > 20 and (a.get("href","").startswith("http") or a.get("href","").startswith("/"))]
    print(f"  {url} -> {len(matched)} 条长链接")
    for t, h in matched[:5]:
        if "/food/" in h or "/retail/" in h or "零食" in t or "食品" in t or "零售" in t:
            print(f"    {h[:80]} | {t[:50]}")