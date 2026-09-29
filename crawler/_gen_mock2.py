import json, os
base = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统"
with open(base + r"\crawler\_data\items_20260929_081714.json", encoding='utf-8') as f:
    items = json.load(f)

evs = []
ev_dir = base + r"\crawler\_data"
ev_files = sorted([f for f in os.listdir(ev_dir) if f.startswith('events_') and f.endswith('.json')])
if ev_files:
    with open(os.path.join(ev_dir, ev_files[-1]), encoding='utf-8') as f:
        evs = json.load(f)

# 清洗 item 字段
for i, it in enumerate(items):
    it['id'] = 'real_' + str(i)
    it['brand_tags'] = it.get('brand_tags') or []
    it['summary'] = it.get('summary') or it.get('title', '')

selected = sorted(items, key=lambda x: x.get('score',0), reverse=True)[:20]
all_items = sorted(items, key=lambda x: x.get('discovered_at',''), reverse=True)

hot_events = sorted(evs, key=lambda x: x.get('hot_score',0), reverse=True)[:10] if evs else []

story = None
if selected:
    it = selected[0]
    story = {
        'id': it.get('id'), 'title': it.get('title'), 'summary': it.get('summary'),
        'url': it.get('url'), 'source_name': it.get('source_name'), 'category': it.get('category'),
        'brand_tags': it.get('brand_tags'), 'event_type': it.get('event_type'),
        'score': it.get('score'), 'published_at': it.get('published_at'),
        'related_items': [x for x in selected if x.get('id') != it.get('id')][:4],
    }

out_lines = []
out_lines.append("// SnackHot mock.js - 真实爬取数据 (2026-09-29)")
out_lines.append("// 数据源: Foodaily 6分类页 + 联商网 + 其他")
out_lines.append("// LLM: Agnes-2.5-flash @ Agnes AI")
out_lines.append("")
out_lines.append("export const mockData = {")
out_lines.append("  '/api/v1/items?mode=selected&limit=20': " + json.dumps({'schemaVersion':2,'data_date':'2026-09-29','count':len(selected),'items':selected}, ensure_ascii=False, indent=2) + ",")
out_lines.append("  '/api/v1/items?mode=all&limit=50': " + json.dumps({'schemaVersion':2,'data_date':'2026-09-29','count':len(all_items),'items':all_items[:50]}, ensure_ascii=False, indent=2) + ",")
out_lines.append("  '/api/v1/hot-topics': " + json.dumps({'schemaVersion':2,'data_date':'2026-09-29','count':len(hot_events),'hot_topics':hot_events}, ensure_ascii=False, indent=2) + ",")
out_lines.append("  '/api/v1/daily/latest': " + json.dumps({'date':'2026-09-29','generated_at':'2026-09-29T08:17:14Z','item_count':len(items),'event_count':len(hot_events),'highlights':[i['title'] for i in selected[:5]],'top_items':selected[:10],'top_events':hot_events[:5]}, ensure_ascii=False, indent=2) + ",")
if story:
    out_lines.append("  '/api/v1/story/" + story['id'] + "': " + json.dumps(story, ensure_ascii=False, indent=2) + ",")
out_lines.append("}")

with open(base + r"\frontend\src\mock.js", 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))
print("OK - mock.js written")
print("items:", len(selected), "selected /", len(all_items), "all")
print("events:", len(hot_events))
