import asyncio, sys, httpx
from bs4 import BeautifulSoup
sys.path.insert(0, r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler")

async def test():
    from sources import ALL_CRAWLERS
    import asyncio as al
    
    for crawler in ALL_CRAWLERS:
        t0 = __import__("time").time()
        try:
            items = await al.wait_for(crawler.fetch(), timeout=25)
            dt = __import__("time").time() - t0
            print(f"  ✅ {crawler.name:20s} {dt:>5.1f}s  {len(items):>3} 条")
        except al.TimeoutError:
            print(f"  ⏳ {crawler.name:20s} TIMEOUT")
        except Exception as e:
            print(f"  ❌ {crawler.name:20s} {str(e)[:50]}")

asyncio.run(test())