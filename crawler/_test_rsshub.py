"""批量测试 RSSHub 零食/零售相关路由"""
import httpx, feedparser, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}

# 公共 RSSHub 实例
HUBS = [
    ("官方", "https://rsshub.app"),
    ("备用1", "https://rsshub.rssforever.com"),
    ("备用2", "https://rsshub.feeded.com"),
    ("备用3", "https://rsshub.pseudoyu.com"),
]

def test(hub, path):
    url = f"{hub}{path}"
    try:
        r = httpx.get(url, headers=UA, timeout=15, follow_redirects=True)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        if len(r.text) < 200:
            return None, "empty"
        feed = feedparser.parse(r.text)
        if not feed.entries:
            return None, f"feed={feed.version} 无条目"
        return feed, f"{len(feed.entries)}条"
    except Exception as e:
        return None, str(e)[:40]

# 目标路由（从 AIHOT 公开的 865 信源结构 + 零食行业实际）
# 先找最靠谱的微信公众号 RSSHub 路由
routes = [
    # ========== 微信公众号（零食行业大号）==========
    ("微信-零食行业", "/wechat/mp/search?keyword=零食行业资讯&limit=10"),
    ("微信-食品饮料", "/wechat/mp/search?keyword=食品饮料行业&limit=10"),
    ("微信-零食量贩", "/wechat/mp/search?keyword=零食量贩&limit=10"),
    ("微信-好想来", "/wechat/mp/search?keyword=好想来&limit=5"),
    ("微信-三只松鼠", "/wechat/mp/search?keyword=三只松鼠+最新消息&limit=5"),
    ("微信-卫龙", "/wechat/mp/search?keyword=卫龙&limit=5"),
    ("微信-良品铺子", "/wechat/mp/search?keyword=良品铺子&limit=5"),
    ("微信-Foodaily", "/wechat/mp/search?keyword=Foodaily每日食品&limit=5"),
    ("微信-零售商业评论", "/wechat/mp/search?keyword=零售商业评论&limit=5"),
    ("微信-食评社", "/wechat/mp/search?keyword=食评社&limit=5"),
    ("微信-快消行业观察", "/wechat/mp/search?keyword=快消行业观察&limit=5"),
    ("微信-联商网", "/wechat/mp/search?keyword=联商网&limit=5"),
    
    # ========== 知乎 ==========
    ("知乎-零食话题", "/zhihu/topic/19554987"),   # 零食话题
    ("知乎-三只松鼠", "/zhihu/topic/19554988"),
    ("知乎-卫龙", "/zhihu/topic/19554989"),
    ("知乎-零售", "/zhihu/topic/19554980"),
    ("知乎热榜-零食", "/zhihu/search/热榜/零食/0/1"),
    
    # ========== B站零食测评 ==========
    ("B站-零食测评分区", "/bilibili/channel/2117883"),  # 食品分区
    ("B站-零食UP主", "/bilibili/channel/2117884"),
    ("B站-三只松鼠官方", "/bilibili/user/video/330093265"),
    ("B站-卫龙官方", "/bilibili/user/video/364989484"),
    
    # ========== 微博 ==========
    ("微博-零食关键词", "/weibo/search/%E9%9B%B6%E9%A3%9F%E8%A1%8C%E4%B8%9A/100103type=1&q=零食"),
    ("微博-三只松鼠超话", "/weibo/super_topic/2245723043"),
    ("微博-卫龙超话", "/weibo/super_topic/3920811534"),
    
    # ========== 抖音 ==========
    ("抖音-好想来品牌号", "/douyin/user/7266790026400262427"),
    ("抖音-零食话题", "/douyin/tag/7204593488912065793"),  # 零食
    
    # ========== 小红书 ==========
    ("小红书-零食测评", "/xiaohongshu/search?keyword=零食测评"),
    ("小红书-零食量贩", "/xiaohongshu/search?keyword=零食量贩"),
    
    # ========== 豆瓣 ==========
    ("豆瓣-零食小组", "/douban/group/topic/263796"),   # 零食与美食
]

print("="*75)
print("RSSHub 全路由测试（先试官方实例）")
print("="*75)

good_results = []
for name, path in routes:
    # 先试官方
    feed, info = test(HUBS[0][1], path)
    if feed:
        titles = [e.get("title","") for e in feed.entries[:3]]
        print(f"  ✅ {name:22s} {info}")
        for t in titles:
            print(f"      - {t[:50]}")
        good_results.append(("official", name, path, info))
    else:
        # 再试备用
        found = False
        for hub_name, hub_url in HUBS[1:]:
            f2, info2 = test(hub_url, path)
            if f2:
                print(f"  ✅ [{hub_name}] {name:22s} {info2}")
                good_results.append((hub_name, name, path, info2))
                found = True
                break
        if not found:
            print(f"  ❌ {name:22s} {info}")
    time.sleep(0.25)

print("\n" + "="*75)
print(f"可接入的 RSSHub 路由: {len(good_results)} 个")
for hub, name, path, info in good_results:
    print(f"  [{hub:8s}] {name:22s} -> {path} ({info})")