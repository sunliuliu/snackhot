"""深挖：联商网（SSL verify=False）+ 每日经济新闻（精确过滤）+ 亿邦动力（找真实文章列表）"""
import httpx, time
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}

WIDE_FOOD = [
    "食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙",
    "辣条","魔芋","奥利奥","烘焙","饼干","糖巧","肉脯","卤味","洽洽",
    "旺旺","绝味","盐津铺子","来伊份","好想来","零食很忙","赵一鸣",
    "量贩零食","零食集合店","快消","食品饮料","快消品","快消品行业",
    "便利店","超市","卖场","便利店行业","门店","零售",
    "消费","品牌","渠道","供应链","营销","加盟","连锁",
]

def get(url, verify=False, headers=None):
    try:
        r = httpx.get(url, headers=headers or UA, timeout=12, follow_redirects=True, verify=verify)
        return r
    except Exception as e:
        return None

# ==============================================
# 1. 联商网（加 verify=False 抓 SSL）
# ==============================================
print("="*70)
print("1. 联商网（零售行业 NO.1）")
print("="*70)
for name, url in [
    ("零售资讯首页", "https://www.linkshop.com.cn/"),
    ("食品餐饮频道", "https://www.linkshop.com.cn/food/"),
    ("快消频道", "https://www.linkshop.com.cn/kc/"),
    ("零食/食品专栏", "https://www.linkshop.com.cn/news/food/"),
]:
    r = get(url, verify=False)
    if r is None:
        print(f"  [ERR] {name}: 网络错误")
        continue
    if r.status_code != 200:
        print(f"  [FAIL] {name}: HTTP {r.status_code}")
        continue
    print(f"  [OK] {name} ({len(r.text)} bytes)")
    soup = BeautifulSoup(r.text, "lxml")
    # 找所有 /news/ 开头的真实文章链接
    art_links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        txt = a.get_text(strip=True)
        if len(txt) < 15: continue
        if href.startswith("//"): href = "https:" + href
        elif href.startswith("/"): href = "https://www.linkshop.com.cn" + href
        if not href.startswith("http"): continue
        if "/news/" in href or "/article/" in href:
            art_links.append((txt, href))
    # 去重
    seen = set()
    uniq = []
    for t, h in art_links:
        if h not in seen:
            seen.add(h)
            uniq.append((t, h))
    snack_n = sum(1 for t,h in uniq if any(k in t for k in WIDE_FOOD))
    print(f"    文章链接: {len(uniq)}, 食品/零售相关: {snack_n}")
    for t, h in uniq[:5]:
        hit = "✅" if any(k in t for k in WIDE_FOOD) else "  "
        print(f"    {hit} {h[:65]} | {t[:45]}")
    time.sleep(0.5)

# ==============================================
# 2. 每日经济新闻（精确过滤食品）
# ==============================================
print("\n" + "="*70)
print("2. 每日经济新闻 - 食品（精确过滤）")
print("="*70)
for name, url in [
    ("食品饮料", "https://www.nbd.com.cn/columns/596"),
    ("快消", "https://www.nbd.com.cn/columns/595"),
    ("消费", "https://www.nbd.com.cn/columns/594"),
]:
    r = get(url)
    if r is None:
        print(f"  [ERR] {name}: 网络错误")
        continue
    if r.status_code != 200:
        print(f"  [FAIL] {name}: HTTP {r.status_code}")
        continue
    soup = BeautifulSoup(r.text, "lxml")
    all_a = soup.find_all("a", href=True)
    arts = []
    for a in all_a:
        txt = a.get_text(strip=True)
        href = a.get("href", "")
        if len(txt) < 15: continue
        if "/articles/" not in href: continue
        if href.startswith("//"): href = "https:" + href
        elif href.startswith("/"): href = "https://www.nbd.com.cn" + href
        arts.append((txt, href))
    seen = set(); uniq = []
    for t, h in arts:
        if h not in seen:
            seen.add(h); uniq.append((t, h))
    # 严格过滤：必须有食品/零食关键词
    strict_kw = ["食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙","辣条","魔芋",
                 "奥利奥","烘焙","饼干","糖巧","肉脯","卤味","洽洽","旺旺","绝味","盐津铺子","来伊份",
                 "好想来","零食很忙","赵一鸣","休闲食品","食品工业","食品饮料"]
    matched = [(t,h) for t,h in uniq if any(k in t for k in strict_kw)]
    print(f"  [OK] {name}: 总文章 {len(uniq)}, 严格匹配零食 {len(matched)}")
    for t, h in matched[:5]:
        print(f"    ✅ {h[:70]} | {t[:55]}")
    # 如果没有严格匹配的，展示宽泛的前几条看看有没有
    if len(matched) == 0 and len(uniq) > 0:
        print(f"    （宽泛看前5条有没有料）")
        for t, h in uniq[:5]:
            print(f"     {h[:70]} | {t[:55]}")
    time.sleep(0.4)

# ==============================================
# 3. 亿邦动力（找真实文章列表）
# ==============================================
print("\n" + "="*70)
print("3. 亿邦动力 - 找真实文章列表")
print("="*70)
for name, url in [
    ("首页", "https://www.ebrun.com/"),
    ("食品频道", "https://www.ebrun.com/retail/food/"),
    ("新零售", "https://www.ebrun.com/retail/"),
    ("食品饮料行业", "https://www.ebrun.com/food/"),   # 换 URL
]:
    r = get(url)
    if r is None:
        print(f"  [ERR] {name}: 网络错误")
        continue
    print(f"  {name}: status={r.status_code} len={len(r.text)}")
    if r.status_code != 200:
        continue
    soup = BeautifulSoup(r.text, "lxml")
    arts = []
    for a in soup.find_all("a", href=True):
        txt = a.get_text(strip=True)
        href = a.get("href", "")
        if len(txt) < 12: continue
        if "/retail/" in href or "/food/" in href or "/news/" in href:
            arts.append((txt, href))
    # 过滤掉 /tc/ 培训广告
    real_arts = [(t,h) for t,h in arts if "/tc/" not in h and len(h) > 18]
    snack = [(t,h) for t,h in real_arts if any(k in t for k in WIDE_FOOD)]
    print(f"    有效文章: {len(real_arts)}, 食品相关: {len(snack)}")
    for t, h in snack[:5]:
        print(f"    ✅ {h[:70]} | {t[:50]}")
    for t, h in real_arts[:3] if not snack else []:
        print(f"     {h[:70]} | {t[:50]}")
    time.sleep(0.4)

# ==============================================
# 4. 更多能跳过 SSL 的零售站
# ==============================================
print("\n" + "="*70)
print("4. 更多跳过 SSL 的零售站")
print("="*70)
extra_sites = [
    ("联商网 - 加盟", "https://www.linkshop.com.cn/join/"),
    ("联商网 - 便利店", "https://www.linkshop.com.cn/store/"),
    ("联商网 - 食品饮料行业", "https://www.linkshop.com.cn/news/food/"),
    ("联商网 - 供应链", "https://www.linkshop.com.cn/scm/"),
    ("零售商业评论 - 备用", "http://www.retail-review.com.cn/"),   # http 试试
    ("中国零售信息网", "https://www.retailing.com/"),
    ("超市发 - 行业", "https://www.linkshop.com.cn/news/supermarket/"),
]
for name, url in extra_sites:
    r = get(url, verify=False)
    if r is None:
        print(f"  [ERR] {name}: 网络错误")
        continue
    if r.status_code != 200:
        print(f"  [FAIL] {name}: HTTP {r.status_code}")
        continue
    soup = BeautifulSoup(r.text, "lxml")
    arts = []
    for a in soup.find_all("a", href=True):
        txt = a.get_text(strip=True)
        href = a.get("href", "")
        if len(txt) < 15: continue
        if "linkshop" in href or "/news/" in href or "/article/" in href or "/retail/" in href or "/food/" in href:
            if "/news/" in href or "/article/" in href or ".shtml" in href or ".html" in href:
                arts.append((txt, href))
    seen = set(); uniq = []
    for t, h in arts:
        h2 = h if h.startswith("http") else "https://" + url.split("/")[2] + h
        if h2 not in seen:
            seen.add(h2); uniq.append((t, h2))
    snack_n = sum(1 for t,h in uniq if any(k in t for k in WIDE_FOOD))
    print(f"  [OK] {name}: {len(uniq)} 条, 食品相关 {snack_n}")
    for t, h in [(t,h) for t,h in uniq if any(k in t for k in WIDE_FOOD)][:3]:
        print(f"    ✅ {h[:70]} | {t[:50]}")
    time.sleep(0.3)