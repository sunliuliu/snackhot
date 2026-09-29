"""直接跑 linkshop 的 fetch 内部逻辑"""
import asyncio, sys, httpx, traceback
sys.path.insert(0, r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler")

async def test():
    from sources.linkshop import LinkshopCrawler, WIDE_KW
    
    c = LinkshopCrawler()
    items = []
    seen = set()
    
    async with httpx.AsyncClient(headers=c.headers, timeout=c.timeout,
                                 follow_redirects=True, verify=False) as client:
        resp = await client.get("http://www.linkshop.com/")
        print(f"status={resp.status_code} len={len(resp.content)}")
        
        # 强制 GBK 解码
        for enc in ["gbk", "gb2312", "gb18030", "utf-8"]:
            try:
                decoded = resp.content.decode(enc)
                if any('\u4e00' <= c2 <= '\u9fff' for c2 in decoded[:2000]):
                    resp.text = decoded
                    print(f"编码: {enc} ✅")
                    break
            except Exception as e:
                print(f"编码 {enc}: {e}")
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")
        print(f"soup created, <a> count={len(soup.find_all('a'))}")
        
        for a in soup.find_all("a", href=True):
            txt = a.get_text(strip=True)
            href = a.get("href", "")
            if len(txt) < 15: continue
            if not (".shtml" in href or "/news/" in href): continue
            if not any(kw in txt for kw in WIDE_KW): continue
            
            if href.startswith("//"): href = "https:" + href
            elif href.startswith("/"): href = "http://www.linkshop.com" + href
            elif not href.startswith("http"): continue
            
            key = href.split("?")[0]
            if key in seen: continue
            seen.add(key)
            print(f"  ✅ {txt[:50]}")
            items.append((txt, href))
        
        print(f"\n共 {len(items)} 条")

asyncio.run(test())