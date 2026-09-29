"""中国糖果网 candy001.com —— 糖果巧克力行业垂直媒体"""
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import httpx
from .base import BaseCrawler
from models import RawItem

class Candy001Crawler(BaseCrawler):
    name = "中国糖果网"
    base_url = "http://www.candy001.com"

    async def fetch(self) -> List[RawItem]:
        items: List[RawItem] = []
        seen = set()
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout,
                                         follow_redirects=True, verify=False) as client:
                resp = await client.get(f"{self.base_url}/")
                if resp.status_code != 200:
                    return []
                decoded_html = resp.content
                for enc in ["gbk", "gb2312", "utf-8"]:
                    try:
                        d = resp.content.decode(enc)
                        if any('\u4e00' <= cc <= '\u9fff' for cc in d[:1000]):
                            decoded_html = d; break
                    except: pass
                soup = BeautifulSoup(decoded_html, "lxml")
                for a in soup.find_all("a", href=True):
                    txt = a.get_text(strip=True)
                    href = a.get("href", "")
                    if len(txt) < 10: continue
                    if not (".html" in href or ".shtml" in href): continue
                    if href.startswith("//"): href = "http:" + href
                    elif href.startswith("/"): href = self.base_url + href
                    elif not href.startswith("http"): continue
                    key = href.split("?")[0]
                    if key in seen: continue
                    seen.add(key)
                    items.append(RawItem(
                        source_name=self.name, title=txt, url=href,
                        published_at=datetime.now(),
                    ))
        except Exception as e:
            print(f"  [糖果网] 失败: {str(e)[:60]}")
        return self._limit(items, 15)