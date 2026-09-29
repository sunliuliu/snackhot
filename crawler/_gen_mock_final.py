import json, os

base = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统"
files = sorted([f for f in os.listdir(base + r"\crawler\_data") if f.startswith('items_') and f.endswith('.json')])
latest = files[-1]
with open(base + r"\crawler\_data" + os.sep + latest, encoding='utf-8') as f:
    items = json.load(f)

# events（如果有）
ev_files = sorted([f for f in os.listdir(base + r"\crawler\_data") if f.startswith('events_') and f.endswith('.json')])
events = []
if ev_files:
    with open(base + r"\crawler\_data" + os.sep + ev_files[-1], encoding='utf-8') as f:
        events = json.load(f)

# 清洗
for i, it in enumerate(items):
    it['id'] = it.get('id') or ('real_' + str(i))
    it['brand_tags'] = it.get('brand_tags') or []
    it['summary'] = it.get('summary') or it.get('title', '')

selected = sorted(items, key=lambda x: x.get('score',0), reverse=True)[:20]
all_items = sorted(items, key=lambda x: x.get('discovered_at',''), reverse=True)
hot_events = sorted(events, key=lambda x: x.get('hot_score',0), reverse=True)[:10] if events else []

out = []
out.append("// SnackHot mock.js - REAL CRAWL DATA (2026-09-29)")
out.append("// Sources: 11 crawlers, 317 items (was 73)")
out.append("// LLM: agnes-2.5-flash 100% success, 42/42 batches")
out.append("// 微博 39 关键词 x Foodaily 6 分类页 x 联商网 x 中国经济网")
out.append("")
out.append("export const mockData = {")
out.append("  '/api/v1/items?mode=selected&limit=20': " + json.dumps({'schemaVersion':2,'data_date':'2026-09-29','count':len(selected),'items':selected}, ensure_ascii=False, indent=2) + ",")
out.append("  '/api/v1/items?mode=all&limit=200': " + json.dumps({'schemaVersion':2,'data_date':'2026-09-29','count':len(all_items),'items':all_items}, ensure_ascii=False, indent=2) + ",")
out.append("  '/api/v1/items?mode=all&limit=50': " + json.dumps({'schemaVersion':2,'data_date':'2026-09-29','count':len(all_items),'items':all_items}, ensure_ascii=False, indent=2) + ",")
out.append("  '/api/v1/hot-topics': " + json.dumps({'schemaVersion':2,'data_date':'2026-09-29','count':len(hot_events),'hot_topics':hot_events}, ensure_ascii=False, indent=2) + ",")
out.append("  '/api/v1/daily/latest': " + json.dumps({'daily':{'date':'2026-09-29','generated_at':'2026-09-29T09:31:47Z','item_count':len(items),'event_count':len(hot_events),'highlights':[i['title'] for i in selected[:8]],'top_items':selected[:15],'top_events':hot_events[:5]}}, ensure_ascii=False, indent=2) + ",")
out.append("  '/api/v1/story/" + selected[0]['id'] + "': " + json.dumps({'id':selected[0]['id'],'title':selected[0]['title'],'summary':selected[0].get('summary',''),'url':selected[0].get('url',''),'source_name':selected[0].get('source_name',''),'category':selected[0].get('category',''),'brand_tags':selected[0].get('brand_tags',[]),'event_type':selected[0].get('event_type',''),'score':selected[0].get('score',0),'published_at':selected[0].get('published_at'),'related_items':selected[1:5]}, ensure_ascii=False, indent=2) + ",")
out.append("}")

with open(base + r"\frontend\src\mock.js", 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print(f"✅ mock.js written: {len(items)} items, {len(hot_events)} events")
print(f"   selected: {len(selected)}, all: {len(all_items)}")
