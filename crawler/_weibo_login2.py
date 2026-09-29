"""启动有头 Playwright，你手动登录微博，60秒后自动保存状态"""
import asyncio, sys
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="zh-CN",
        )
        await context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>false});window.chrome={runtime:{}};")
        
        page = await context.new_page()
        await page.goto("https://weibo.com/", wait_until="domcontentloaded")
        
        print("\n" + "="*60)
        print("🚨 微博浏览器窗口应该已经弹出了！")
        print("   请在弹出的浏览器里登录你的微博账号")
        print("   60 秒后会自动保存登录状态")
        print("="*60 + "\n", flush=True)
        
        # 倒计时
        for i in range(60, 0, -10):
            print(f"   还剩 {i} 秒...", flush=True)
            await asyncio.sleep(10)
        
        # 验证
        await page.goto("https://s.weibo.com/weibo?q=%E4%B8%89%E5%8F%AA%E6%9D%BE%E9%BC%A0&typeall=1", timeout=30000)
        await page.wait_for_timeout(2000)
        
        current_url = page.url
        print(f"\n当前 URL: {current_url[:60]}", flush=True)
        
        if "passport" in current_url or "login" in current_url.lower():
            print("❌ 未登录成功", flush=True)
        else:
            cards = await page.query_selector_all(".card-wrap")
            print(f"✅ 登录成功！抓到 {len(cards)} 条微博", flush=True)
            state_path = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler\_weibo_state.json"
            await context.storage_state(path=state_path)
            print(f"✅ Storage state 已保存: {state_path}", flush=True)
        
        print("5秒后关闭...", flush=True)
        await asyncio.sleep(5)
        await browser.close()

asyncio.run(main())