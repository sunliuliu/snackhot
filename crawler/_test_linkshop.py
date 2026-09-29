"""修复联商网编码 + 找零售频道入口"""
import httpx, time
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}
WIDE_FOOD = ["食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙",
             "辣条","魔芋","奥利奥","烘焙","饼干","糖巧","肉脯","卤味","洽洽",
             "旺旺","绝味","盐津铺子","来伊份","好想来","零食很忙","赵一鸣",
             "休闲食品","食品工业","食品饮料","快消","便利店","量贩","零售",
             "门店","加盟","连锁","供应链","渠道","营销","消费","品牌","快消品"]

r = httpx.get("http://www.linkshop.com/", headers=UA, timeout=10, verify=False)
raw = r.content

# 探测编码
decoded = None
for enc in ["gbk", "gb2312", "gb18030", "big5", "utf-8"]:
    try:
        d = raw.decode(enc)
        if any('\u4e00' <= c <= '\u9fff' for c in d[:2000]):
            decoded = d
            print(f"编码探测: ✅ {enc}")
            break
    except: pass

if not decoded:
    print("编码探测失败")
    exit()

soup = BeautifulSoup(decoded, "lxml")

# 所有文章
arts = []
for a in soup.find_all("a", href=True):
    txt = a.get_text(strip=True)
    href = a.get("href", "")
    if len(txt) < 15: continue
    if ".shtml" in href or "/news/" in href:
        if href.startswith("//"): href = "https:" + href
        elif href.startswith("/"): href = "http://www.linkshop.com" + href
        arts.append((txt, href))
seen = set(); uniq = []
for t, h in arts:
    if h not in seen and h.startswith("http"):
        seen.add(h); uniq.append((t, h))

snack = [(t,h) for t,h in uniq if any(k in t for k in WIDE_FOOD)]
print(f"\n总文章 {len(uniq)}, 食品/零售相关 {len(snack)}")
print("\n=== 零售/食品文章 ===")
for t, h in snack[:15]:
    print(f"  ✅ {t[:60]}")
    print(f"     {h[:70]}")

# 频道入口
print("\n=== 频道入口 ===")
for a in soup.find_all("a", href=True):
    txt = a.get_text(strip=True)
    href = a.get("href", "")
    if len(txt) >= 4 and any(k in txt for k in ["食品","零售","快消","便利店","超市","零食","餐饮","加盟"]):
        print(f"  {txt:15s} -> {href[:60]}")