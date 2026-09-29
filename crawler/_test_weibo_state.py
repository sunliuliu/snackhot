"""Playwright + storage state 测试微博搜索"""
import asyncio, json
from playwright.async_api import async_playwright

# 从 browser_use 浏览器导出的 cookie 拼成 storage state
storage_state = {
    "cookies": [
        {"name": "_s_tentry", "value": "open.weibo.com", "domain": ".weibo.com", "path": "/"},
        {"name": "Apache", "value": "2232659429518.3267.1790663717369", "domain": ".weibo.com", "path": "/"},
        {"name": "SINAGLOBAL", "value": "2232659429518.3267.1790663717369", "domain": ".weibo.com", "path": "/"},
        {"name": "ULV", "value": "1790663717380:1:1:1:2232659429518.3267.1790663717369:", "domain": ".weibo.com", "path": "/"},
        {"name": "PC_TOKEN", "value": "927576b640", "domain": ".weibo.com", "path": "/"},
        {"name": "SUBP", "value": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WWHpT3MFaTr-XqUj045CY3O5NHD95Qp1K.EeoecS05pWs4DqcjxBJ8EdJHXUG.LxKBLBonLBoqt", "domain": ".weibo.com", "path": "/"},
        {"name": "ALF", "value": "02_1793255820", "domain": ".weibo.com", "path": "/"},
    ],
    "origins": []
}

state_path = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler\_weibo_state.json"
with open(state_path, "w") as f:
    json.dump(storage_state, f)

print(f"Storage state saved to {state_path}", flush=True)

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="zh-CN",
            storage_state=state_path,  # ← 关键！复用登录态
        )
        await context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>false});window.chrome={runtime:{}};")
        
        page = await context.new_page()
        
        queries = ["三只松鼠", "卫龙", "好想来", "零食行业"]
        
        for q in queries:
            url = f"https://s.weibo.com/weibo?q={q}&typeall=1&suball=1"
            try:
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                
                cur = page.url
                print(f"\n{'='*60}")
                print(f"搜索: {q}")
                print(f"  URL: {cur[:60]}")
                
                if "passport" in cur or "login" in cur.lower():
                    print(f"  ❌ Cookie 失效")
                    continue
                
                cards = await page.query_selector_all(".card-wrap")
                print(f"  ✅ 抓到 {len(cards)} 条微博卡片")
                
                items = await page.evaluate("""() => {
                    const r = [];
                    document.querySelectorAll('.card-wrap').forEach((c, i) => {
                        if (i < 5) {
                            const t = c.querySelector('p[node-type*="feed_list_content"], .content');
                            const text = t ? t.innerText.trim().substring(0, 100) : '';
                            // 转评赞数
                            const nums = [];
                            c.querySelectorAll('a[action-data], .woo-box-flex a').forEach(a => {
                                const n = a.textContent.trim();
                                if (n && /^[0-9]+$/.test(n)) nums.push(n);
                            });
                            if (text) r.push({idx:i, text, nums: nums.slice(-3)});
                        }
                    });
                    return r;
                }""")
                
                for it in items:
                    print(f"    #{it['idx']} [转评赞:{it['nums']}] {it['text'][:80]}")
                    
            except Exception as e:
                print(f"  ❌ {str(e)[:60]}")
        
        await browser.close()

asyncio.run(test())