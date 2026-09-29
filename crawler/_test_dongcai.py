"""深挖东财 API"""
import httpx, json

UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.eastmoney.com/"}

# 1. 滚动新闻 API —— 看看缺什么参数
print("=== 东财滚动新闻 API ===")
r = httpx.get("https://np-listapi.eastmoney.com/comm/web/getNewsByColumns", params={
    "client": "web", "biz": "web_news_col", "column": "350",
    "order": "1", "needInteractData": "0", "page_index": "1", "page_size": "30",
}, headers=UA, timeout=10)
print(f"  status={r.status_code} body={r.text[:300]}")

# 2. 公告 API（行业，s_node=48 是食品饮料？）
print("\n=== 东财行业公告 API ===")
r = httpx.get("https://np-anotice-stock.eastmoney.com/api/security/ann", params={
    "page_size": "30", "page_index": "1",
    "ann_type": "SHA", "client_source": "web",
    "f_node": "0", "s_node": "48",
}, headers={**UA, "Referer": "https://data.eastmoney.com/"}, timeout=10)
d = r.json()
print(f"  code={d.get('code')} msg={d.get('message')}")
data_list = d.get("data", {}).get("list") or []
print(f"  共 {len(data_list)} 条")
kw = ["食品","饮料","零食","糖果","巧克力","坚果","三只松鼠","良品","卫龙","辣条","魔芋","奥利奥","烘焙","饼干","糖巧","肉脯","卤味","洽洽","旺旺","绝味","盐津铺子","来伊份"]
for a in data_list[:15]:
    title = a.get("title", "")
    sec = a.get("secName") or a.get("stock_name") or ""
    hit = "✅" if any(k in title or k in sec for k in kw) else ""
    print(f"  {hit} [{sec}] {title[:60]}")
print("\n  全量公司名去重：")
secs = sorted(set((a.get("secName") or a.get("stock_name") or "") for a in data_list))
print(f"  {secs}")