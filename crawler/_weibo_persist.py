"""启动持久化 Playwright，登录一次永久有效"""
import asyncio
from playwright.async_api import async_playwright

USER_DATA_DIR = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler\.weibo_profile"

async def main():
    async with async_playwright() as p:
        # 持久化浏览器（cookie 会自动保存到 USER_DATA_DIR）
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport=None,  # 最大化
            locale="zh-CN",
        )
        await context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>false});window.chrome={runtime:{}};")
        
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://s.weibo.com/weibo?q=%E4%B8%89%E5%8F%AA%E6%9D%BE%E9%BC%A0&typeall=1", wait_until="domcontentloaded")
        
        print("\n" + "="*60, flush=True)
        print("🚨 【第 1 次运行】浏览器窗口应该已经弹出！", flush=True)
        print("   请在浏览器里登录微博账号（扫码或手机号）", flush=True)
        print("   登录成功后，直接关闭浏览器窗口即可", flush=True)
        print("   下次运行爬虫就不需要再登录了！", flush=True)
        print("="*60, flush=True)
        print("\n我会等 180 秒让你登录...", flush=True)
        
        # 等用户登录。最多 180 秒，期间每秒检查 URL
        for i in range(180):
            await asyncio.sleep(1)
            cur = page.url
            if "passport" not in cur and "login" not in cur.lower() and "s.weibo.com" in cur:
                print(f"\n✅ 检测到登录成功！URL: {cur[:60]}", flush=True)
                # 验证一下能不能抓到卡片
                await page.wait_for_timeout(2000)
                cards = await page.query_selector_all(".card-wrap")
                print(f"   抓到 {len(cards)} 条微博", flush=True)
                break
            if i > 0 and i % 30 == 0:
                print(f"   已等待 {i} 秒...", flush=True)
        else:
            print("\n⏰ 180 秒超时", flush=True)
        
        print("\n5 秒后自动关闭并保存状态...", flush=True)
        await asyncio.sleep(5)
        await context.close()
        print(f"✅ 状态已保存到: {USER_DATA_DIR}", flush=True)

asyncio.run(main())