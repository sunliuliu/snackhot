"""启动有头 Playwright，你手动登录微博，我保存 storage state"""
import asyncio, json, time
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # 有头模式 + 隐藏自动化特征
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="zh-CN",
        )
        
        # 注入脚本隐藏 webdriver 特征
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            window.chrome = { runtime: {} };
        """)
        
        page = await context.new_page()
        
        # 打开微博首页，等你登录
        await page.goto("https://weibo.com/", wait_until="domcontentloaded")
        
        print("\n" + "="*60)
        print("🚨 请在打开的浏览器窗口里手动登录微博！")
        print("   登录完成后，回到这个终端按 [Enter] 键继续")
        print("="*60 + "\n")
        
        # 等用户按回车
        input("按 Enter 继续...")
        
        # 验证登录状态
        await page.goto("https://s.weibo.com/weibo?q=%E4%B8%89%E5%8F%AA%E6%9D%BE%E9%BC%A0&typeall=1", timeout=30000)
        await page.wait_for_timeout(2000)
        
        current_url = page.url
        print(f"\n当前 URL: {current_url[:60]}")
        
        if "passport" in current_url or "login" in current_url.lower():
            print("❌ 检测到还没登录，请先登录再重试")
        else:
            # 提取验证
            cards = await page.query_selector_all(".card-wrap")
            print(f"✅ 登录成功！抓到 {len(cards)} 条微博")
            
            # 保存 storage state
            state_path = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler\_weibo_state.json"
            await context.storage_state(path=state_path)
            print(f"✅ Storage state 已保存到: {state_path}")
        
        print("\n浏览器将在 5 秒后关闭...")
        await asyncio.sleep(5)
        await browser.close()

asyncio.run(main())