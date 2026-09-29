import json, os, sys
from collections import Counter

# 读真实数据
base = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统"
with open(base + r"\crawler\_data\items_20260929_081714.json", encoding='utf-8') as f:
    items = json.load(f)

# 读 events (最新的)
evs = []
ev_dir = base + r"\crawler\_data"
ev_files = sorted([f for f in os.listdir(ev_dir) if f.startswith('events_') and f.endswith('.json')])
if ev_files:
    with open(os.path.join(ev_dir, ev_files[-1]), encoding='utf-8') as f:
        evs = json.load(f)

# 转成前端需要的 mockData 结构
# 需要: { "/api/v1/items?xxx": {...}, "/api/v1/hot-topics": {...} }

# === items ===
selected = sorted(items, key=lambda x: x.get('score',0), reverse=True)[:20]
all_items = sorted(items, key=lambda x: x.get('discovered_at',''), reverse=True)

# 给每个 item 加 id 和 selected 标记
for i, it in enumerate(items):
    it['id'] = f"real_{i}"
    it['selected'] = it in selected
    # 补 brand_tags 默认空数组
    if not it.get('brand_tags'):
        it['brand_tags'] = []
    if not it.get('summary'):
        it['summary'] = it.get('title', '')

items_selected_resp = {
    "schemaVersion": 2,
    "data_date": "2026-09-29",
    "count": len(selected),
    "items": selected,
}

items_all_resp = {
    "schemaVersion": 2,
    "data_date": "2026-09-29",
    "count": len(all_items),
    "items": all_items[:50],
}

# === hot topics ===
if evs:
    hot_events = sorted(evs, key=lambda x: x.get('hot_score',0), reverse=True)[:10]
else:
    # 从 items 聚类简单造热点
    hot_events = []

hot_resp = {
    "schemaVersion": 2,
    "data_date": "2026-09-29",
    "count": len(hot_events),
    "hot_topics": hot_events,
}

# === daily ===
daily_items = selected[:10]
daily_resp = {
    "date": "2026-09-29",
    "generated_at": "2026-09-29T08:17:14Z",
    "item_count": len(items),
    "event_count": len(hot_events),
    "highlights": [it['title'] for it in daily_items[:5]],
    "top_items": daily_items,
    "top_events": hot_events[:5],
}

# === story 详情 ===
story_resp = None
if items:
    it = selected[0]
    story_resp = {
        "id": it.get('id'),
        "title": it.get('title'),
        "summary": it.get('summary'),
        "url": it.get('url'),
        "source_name": it.get('source_name'),
        "category": it.get('category'),
        "brand_tags": it.get('brand_tags'),
        "event_type": it.get('event_type'),
        "score": it.get('score'),
        "published_at": it.get('published_at'),
        "related_items": [x for x in selected if x.get('id') != it.get('id')][:4],
    }

print("// SnackHot mock.js —— 真实爬取数据 (2026-09-29)")
print("// 数据源: 8 crawlers (Foodaily 6分类页 + 联商网 + 微博29关键词 + 巨潮 + 东财 + 新浪 + 糖果网 + 36氪)")
print("// LLM: Agnes-2.5-flash @ Agnes AI (100% 成功率)")
print()
print("export const mockData = {")
print("  // === Items 最新精选 (首页) ===")
print(f"  '/api/v1/items?mode=selected&limit=20': {json.dumps(items_selected_resp, ensure_ascii=False, indent=2)},")
print()
print("  // === Items 全部动态 ===")
print(f"  '/api/v1/items?mode=all&limit=50': {json.dumps(items_all_resp, ensure_ascii=False, indent=2)},")
print()
print("  // === Hot Topics 热点榜 ===")
print(f"  '/api/v1/hot-topics': {json.dumps(hot_resp, ensure_ascii=False, indent=2)},")
print()
print("  // === Daily 每日早报 ===")
print(f"  '/api/v1/daily/latest': {json.dumps(daily_resp, ensure_ascii=False, indent=2)},")
print()
print("  // === Item Story 详情页 ===")
if story_resp:
    print(f"  '/api/v1/story/{story_resp[\"id\"]}': {json.dumps(story_resp, ensure_ascii=False, indent=2)},")
print("}")

# 同时导出 mock 中引用的 BASE_ITEMS
# 但 pages 用的是 api.getItems 不直接 import BASE_ITEMS
