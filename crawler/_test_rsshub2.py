"""精准测 RSSHub —— 只试官方实例，每条 8s 超时"""
import httpx, feedparser, time

UA = {"User-Agent": "Mozilla/5.0"}
BASE = "https://rsshub.app"

WIDE_KW = ["食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙",
           "辣条","魔芋","奥利奥","烘焙","饼干","糖巧","肉脯","卤味","洽洽",
           "旺旺","绝味","盐津铺子","来伊份","好想来","零食很忙","赵一鸣",
           "休闲食品","食品工业","食品饮料","快消","便利店","量贩","零售",
           "门店","加盟","连锁","供应链","渠道","营销","消费","品牌"]

def quick_test(path):
    try:
        r = httpx.get(f"{BASE}{path}", headers=UA, timeout=8, follow_redirects=True)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        if len(r.text) < 300:
            return None, "empty"
        feed = feedparser.parse(r.text)
        if not feed.entries:
            return None, "0 entries"
        return feed, f"{len(feed.entries)}条 v={feed.version}"
    except Exception as e:
        return None, str(e)[:40]

routes = [
    # ===== 微信搜索（最靠谱，直接搜关键词）=====
    ("微信-零食行业",           "/wechat/mp/search?keyword=零食行业资讯&limit=8"),
    ("微信-食品饮料行业",       "/wechat/mp/search?keyword=食品饮料行业&limit=8"),
    ("微信-零食量贩",           "/wechat/mp/search?keyword=零食量贩&limit=8"),
    ("微信-三只松鼠",           "/wechat/mp/search?keyword=三只松鼠+最新消息&limit=5"),
    ("微信-卫龙",               "/wechat/mp/search?keyword=卫龙&limit=5"),
    ("微信-Foodaily",           "/wechat/mp/search?keyword=Foodaily每日食品&limit=5"),
    ("微信-联商网",             "/wechat/mp/search?keyword=联商网&limit=5"),
    ("微信-零售商业评论",       "/wechat/mp/search?keyword=零售商业评论&limit=5"),
    ("微信-快消行业观察",       "/wechat/mp/search?keyword=快消行业观察&limit=5"),
    
    # ===== 知乎 =====
    ("知乎-零食话题",           "/zhihu/topic/19554987"),
    ("知乎-零售话题",           "/zhihu/topic/19554980"),
    ("知乎热榜-零食",           "/zhihu/search/热榜/零食/0/8"),
    
    # ===== B站 =====
    ("B站-食品分区",            "/bilibili/channel/2117883"),
    ("B站-零食测评分区",        "/bilibili/channel/2117884"),
    
    # ===== 微博 =====
    ("微博-零食搜索",           "/weibo/search/%E9%9B%B6%E9%A3%9F%E8%A1%8C%E4%B8%9A/100103"),
    
    # ===== 豆瓣 =====
    ("豆瓣-零食与美食小组",     "/douban/group/topic/263796"),
]

print("="*70)
print(f"{'NAME':25s} {'STATUS':40s} {'TITLES'}")
print("="*70)

good = []
for name, path in routes:
    t0 = time.time()
    feed, info = quick_test(path)
    dt = time.time() - t0
    
    if feed:
        titles = [e.get("title","") for e in feed.entries]
        snack_n = sum(1 for t in titles if any(k in t for k in WIDE_KW))
        marker = "🎯" if snack_n > 0 else "✅"
        print(f"{marker} {name:23s} {info + f' ({dt:.1f}s)':38s} 零食相关={snack_n}")
        for t in titles[:2]:
            hit = "  [SNACK]" if any(k in t for k in WIDE_KW) else ""
            print(f"      - {t[:55]}{hit}")
        good.append((name, path, info, snack_n))
    else:
        print(f"  ❌ {name:23s} {info[:38]} ({dt:.1f}s)")
    time.sleep(0.2)

print("\n" + "="*70)
print(f"可接入: {len(good)}/{len(routes)}")
for name, path, info, sn in sorted(good, key=lambda x: -x[3]):
    print(f"  [snack={sn}] {name:22s} -> {path}")