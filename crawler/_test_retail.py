"""批量测试零售类站点哪些能静态爬取"""
import httpx, time
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}

# 宽泛零食+零售关键词
SNACK_KW = ["零食","坚果","糖果","巧克力","饼干","糕点","膨化","魔芋","辣条","卫龙","三只松鼠","良品","百草味"]
RETAIL_KW = ["零食量贩","量贩零食","零食店","零食集合店","好想来","零食很忙","赵一鸣","零食代","怡佳仁","贪吃嘴","连锁","加盟","门店"]
FOOD_RETAIL = ["食品","饮料","食品饮料","餐饮","快消"]

def test_site(name, url, selector=None, title_filter=None):
    """测试一个站点，返回 (状态, 条目数, 示例)"""
    try:
        r = httpx.get(url, headers=UA, timeout=10, follow_redirects=True)
        if r.status_code != 200:
            return f"[FAIL] {name}: HTTP {r.status_code}", 0, []
        if len(r.text) < 1000:
            return f"[SKIP] {name}: content too short", 0, []
        soup = BeautifulSoup(r.text, "lxml")
        all_a = soup.find_all("a", href=True)
        good = []
        for a in all_a:
            txt = a.get_text(strip=True)
            href = a.get("href", "")
            if len(txt) < 12:
                continue
            if selector and selector not in href and not any(selector in c for c in a.get("class", [])):
                continue
            good.append((txt, href))
        return None, len(good), good[:5]
    except Exception as e:
        return f"[ERR] {name}: {str(e)[:60]}", 0, []


sites = [
    # ============ 零售专业媒体 ============
    ("联商网 - 零售资讯", "https://www.linkshop.com.cn/retail/"),
    ("联商网 - 食品餐饮", "https://www.linkshop.com.cn/food/"),
    ("联商网 - 快消", "https://www.linkshop.com.cn/kc/"),
    ("零售商业评论", "https://www.lingshou-pinglun.com/"),
    ("龙商网 - 资讯", "https://www.linkshop.com.cn/"),
    ("超市周刊", "https://www.linkshop.com.cn/channel/"),
    
    # ============ 亿邦动力（之前 RSS 没条目，试试网页）============
    ("亿邦动力 - 食品", "https://www.ebrun.com/retail/food/"),
    ("亿邦动力 - 新零售", "https://www.ebrun.com/retail/"),
    ("亿邦动力 - 快消", "https://www.ebrun.com/retail/fmcg/"),
    ("亿邦动力 - 行业", "https://www.ebrun.com/retail/industry/"),
    ("亿邦动力首页", "https://www.ebrun.com/"),
    
    # ============ 快消行业媒体 ============
    ("快消网", "https://www.fmcgchina.com/"),
    ("新消费内参", "https://www.newretaildaily.com/"),
    ("新榜 - 零售", "https://www.newrank.cn/topics/retail"),
    ("窄门餐眼 - 零食", "https://www.canyinfranchise.com/"),
    
    # ============ 电商数据类 ============
    ("天猫超市 - 零食热销", "https://chaoshi.detail.tmall.com/"),
    ("京东超市 - 零食", "https://channel.jd.com/chaoshi.html"),
    ("抖音电商 - 零食品牌榜", "https://trends.microapp.bytedance.com/"),
    
    # ============ 行业媒体 ============
    ("第一财经 - 消费", "https://www.yicai.com/news/consume.html"),
    ("界面新闻 - 消费", "https://www.jiemian.com/lists/84.html"),
    ("澎湃新闻 - 消费", "https://www.thepaper.cn/channel_25951"),
    ("每日经济新闻 - 食品", "https://www.nbd.com.cn/columns/596"),
    ("搜狐 - 食品", "https://www.sohu.com/category/food/"),
    
    # ============ 量贩零食专门站 ============
    ("好想来官网 - 新闻", "https://www.haoxiaolai.com/news.html"),
    ("零食很忙官网 - 动态", "https://www.lingxiansd.com/news.html"),
]

print("="*70)
print("零售类站点批量测试")
print("="*70)

good_sites = []
for name, url in sites:
    err, n, samples = test_site(name, url)
    if err:
        print(err)
        continue
    # 统计有零食/零售关键词的条目
    snack_n = sum(1 for t,h in samples if any(k in t for k in SNACK_KW))
    retail_n = sum(1 for t,h in samples if any(k in t for k in RETAIL_KW))
    tag = f"snack={snack_n} retail={retail_n}"
    if n >= 3:
        good_sites.append((name, url, n))
    print(f"[OK] {name:30s} entries={n:>3}  {tag}")
    for t,h in samples[:3]:
        hit = "✅" if any(k in t for k in SNACK_KW+RETAIL_KW) else "  "
        print(f"     {hit} {h[:65]} | {t[:45]}")
    print()
    time.sleep(0.3)

print("="*70)
print(f"推荐接入 ({len(good_sites)} 个):")
for name, url, n in good_sites:
    print(f"  ✅ {name:30s} {n:>3} entries  {url[:60]}")