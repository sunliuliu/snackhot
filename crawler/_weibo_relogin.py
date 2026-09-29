"""重新登录微博（持久化浏览器）—— 简单版"""
import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright

USER_DATA_DIR = str(Path(__file__).parent / ".weibo_profile")

async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport=None,
            locale="zh-CN",
        )
        await context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>false});window.chrome={runtime:{}};")
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        # 直接去微博搜索页（已登录的话直接出结果，没登录的话自动跳 passport）
        await page.goto("https://s.weibo.com/weibo?q=%E4%B8%89%E5%8F%AA%E6%9D%BE%E9%BC%A0&typeall=1", wait_until="domcontentloaded")
        
        cur = page.url
        print(f"\n当前 URL: {cur[:60]}", flush=True)
        
        if "passport" in cur or "login" in cur.lower():
            print("\n🚨 浏览器窗口应该已经弹出！请扫码/输入手机号登录微博", flush=True)
            print("   登录成功后程序会自动检测到...", flush=True)
            
            for i in range(180):
                await asyncio.sleep(1)
                cur = page.url
                if "s.weibo.com" in cur and "passport" not in cur:
                    print(f"\n✅ 登录成功！", flush=True)
                    # 点一下"综合" tab 确保页面加载
                    await page.wait_for_timeout(3000)
                    cards = await page.query_selector_all(".card-wrap")
                    print(f"   抓到 {len(cards)} 条微博，状态已自动保存", flush=True)
                    break
                if i > 0 and i % 30 == 0:
                    print(f"   等待中... {i}s", flush=True)
        else:
            cards = await page.query_selector_all(".card-wrap")
            print(f"\n✅ 已经是登录状态！抓到 {len(cards)} 条微博", flush=True)
        
        print("\n状态已保存到 .weibo_profile/", flush=True)
        print("5 秒后关闭...", flush=True)
        await asyncio.sleep(5)
        await context.close()

asyncio.run(main())