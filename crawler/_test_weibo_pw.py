"""Playwright 持久化浏览器测试 —— 复用刚才的登录状态"""
import asyncio, json, sys
sys.path.insert(0, r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler")

from playwright.async_api import async_playwright

USER_DATA_DIR = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler\.weibo_profile"

# 零食行业搜索关键词（从 SOURCES.md 扩展）
QUERIES = [
    "三只松鼠", "良品铺子", "卫龙", "盐津铺子", "洽洽",
    "好想来", "零食很忙", "赵一鸣", "零食代", "来伊份",
    "魔芋零食", "辣条", "坚果炒货", "肉脯卤味", "糖果巧克力",
    "饼干烘焙", "休闲食品", "零食行业", "量贩零食", "零食连锁",
    "胖东来零食", "奥利奥联名", "新品发布",
]

async def crawl_weibo():
    results = []
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=True,  # 持久化浏览器可以 headless 了！cookie 已经记住
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="zh-CN",
        )
        await context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>false});window.chrome={runtime:{}};")
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        for q in QUERIES[:10]:  # 先测 10 个
            url = f"https://s.weibo.com/weibo?q={q}&typeall=1&suball=1"
            try:
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(1500)
                
                cur = page.url
                if "passport" in cur or "login" in cur.lower():
                    print(f"  ⚠️  Cookie 过期了（{q}）", flush=True)
                    break
                
                cards = await page.query_selector_all(".card-wrap")
                print(f"\n【{q}】{len(cards)} 条", flush=True)
                
                items = await page.evaluate("""(keyword) => {
                    const r = [];
                    document.querySelectorAll('.card-wrap').forEach((c, i) => {
                        // 跳过置顶广告
                        if (c.querySelector('.card-act')?.innerText.includes('推广')) return;
                        
                        const t = c.querySelector('p[node-type*="feed_list_content"], .content');
                        const text = t ? t.innerText.trim().replace(/\\n/g, ' ') : '';
                        if (!text || text.length < 15) return;
                        
                        // 转评赞
                        const nums = [];
                        c.querySelectorAll('a.woo-box-item-flex, .box a[href]').forEach(a => {
                            const n = a.textContent.trim();
                            if (n && /^[0-9]+$/.test(n)) nums.push(parseInt(n));
                        });
                        
                        // 时间
                        const timeEl = c.querySelector('a[href*="/status/"]');
                        const timeText = timeEl ? timeEl.textContent.trim() : '';
                        
                        // 用户
                        const userEl = c.querySelector('a.name, a[href*="/u/"], .m-text-box a');
                        const userName = userEl ? userEl.textContent.trim() : '';
                        
                        // 链接
                        const link = timeEl ? timeEl.href : '';
                        
                        r.push({
                            keyword,
                            text: text.substring(0, 300),
                            fullText: text,
                            repost: nums[0] || 0,
                            comment: nums[1] || 0,
                            like: nums[2] || 0,
                            time: timeText,
                            user: userName,
                            link,
                            score: (nums[0]||0)*3 + (nums[1]||0)*2 + (nums[2]||0)  // 热度分 = 转发×3 + 评论×2 + 点赞
                        });
                    });
                    return r;
                }""", q)
                
                for it in items:
                    results.append(it)
                    marker = "🔥" if it['score'] > 100 else "✅"
                    print(f"  {marker} 转{it['repost']}评{it['comment']}赞{it['like']} [{it['score']}] {it['text'][:60]}", flush=True)
                    
            except Exception as e:
                print(f"  ❌ {q}: {str(e)[:50]}", flush=True)
        
        await context.close()
    
    # 去重 + 按热度排序
    seen = set()
    unique = []
    for it in results:
        if it['text'][:30] not in seen:
            seen.add(it['text'][:30])
            unique.append(it)
    
    unique.sort(key=lambda x: -x['score'])
    
    print(f"\n\n{'='*60}", flush=True)
    print(f"📊 总计: {len(results)} 条 → 去重 {len(unique)} 条", flush=True)
    print(f"🔥 Top 5 热度最高:", flush=True)
    for it in unique[:5]:
        print(f"   [{it['keyword']}] score={it['score']} {it['text'][:55]}", flush=True)
    
    return unique

if __name__ == "__main__":
    asyncio.run(crawl_weibo())