"""诊断东方财富真实 DOM 结构"""
import httpx
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}
urls = [
    ("财经要闻", "https://finance.eastmoney.com/a/czqyw.html"),
    ("公司新闻", "https://finance.eastmoney.com/a/cgsxw.html"),
    ("滚动新闻", "https://finance.eastmoney.com/a/ccjxw.html"),
]
for name, url in urls:
    r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
    print(f"\n=== {name} {url} ===")
    print(f"  final_url={str(r.url)[:80]} status={r.status_code} len={len(r.text)}")
    soup = BeautifulSoup(r.text, "lxml")
    # 看 script 里有没有 __NEXT_DATA__（可能是 Next.js 站点）
    scripts = soup.find_all("script")
    for s in scripts:
        txt = s.string or ""
        if len(txt) > 5000:
            print(f"  script len={len(txt)} (可能是 SSR 数据)")
            break
    # 找所有 ul/li 列表
    for tag in ["ul", "div", "section"]:
        found = soup.find_all(tag)
        for f in found:
            cls = f.get("class", [])
            if cls and any(kw in " ".join(cls).lower() for kw in ["news", "list", "item", "feed"]):
                print(f"  {tag}.{' '.join(cls)} -> children={len(list(f.children))}")
                links = f.find_all("a", href=True)[:3]
                for a in links:
                    print(f"    a: {a.get('href','')[:60]} | {a.get_text(strip=True)[:40]}")
                break