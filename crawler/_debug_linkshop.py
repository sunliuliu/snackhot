import asyncio, sys, json, httpx
from bs4 import BeautifulSoup
sys.path.insert(0, r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler")

async def test():
    from sources.linkshop import LinkshopCrawler
    
    c = LinkshopCrawler()
    print(f"name={c.name} headers={c.headers} timeout={c.timeout}")
    
    # 手动
    async with httpx.AsyncClient(headers=c.headers, timeout=15, follow_redirects=True, verify=False) as client:
        resp = await client.get("http://www.linkshop.com/")
        print(f"\n手动抓: status={resp.status_code} len={len(resp.text)}")
    
    # fetcher
    items = await c.fetch()
    print(f"\nfetcher: {len(items)} 条")

asyncio.run(test())