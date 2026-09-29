"""测微博公开搜索页面能不能爬"""
import httpx, time, re

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

queries = [
    "零食行业",
    "三只松鼠",
    "卫龙",
    "魔芋零食",
]

for q in queries:
    url = f"https://s.weibo.com/weibo?q={q}&typeall=1&suball=1&Refer=g"
    print(f"\n{'='*60}")
    print(f"搜索: {q}")
    print(f"URL: {url}")
    try:
        r = httpx.get(url, headers=UA, timeout=15, follow_redirects=True)
        print(f"  status={r.status_code}  len={len(r.text)}  final_url={str(r.url)[:60]}")
        
        if r.status_code == 200 and len(r.text) > 1000:
            # 检查有没有反爬
            if "weibo.com/signup/signup.php" in str(r.url):
                print("  ❌ 被重定向到登录页了")
            elif "sorry" in r.text.lower() or "passport" in str(r.url):
                print("  ❌ 反爬了")
            else:
                # 简单统计一下
                cards = re.findall(r'<div[^>]*class="card-wrap"', r.text)
                print(f"  ✅ 抓到 {len(cards)} 条卡片")
                # 提取前几个标题
                titles = re.findall(r'<a[^>]*class="s-text-node"[^>]*>(.*?)</a>', r.text, re.DOTALL)
                if not titles:
                    titles = re.findall(r'<p[^>]*class=".*text.*"[^>]*>(.*?)</p>', r.text, re.DOTALL)
                for t in titles[:3]:
                    clean = re.sub(r'<[^>]+>', '', t).strip()[:60]
                    if clean:
                        print(f"    - {clean}")
        else:
            print(f"  ❌ 状态异常")
    except Exception as e:
        print(f"  ❌ {str(e)[:50]}")
    time.sleep(1.5)