import json, glob, os
items_f = sorted(glob.glob("c:/Users/user/.trae-cn/worktrees/零食行业资讯热点系统/crawler/_data/items_*.json"))[-1]
evts_f = sorted(glob.glob("c:/Users/user/.trae-cn/worktrees/零食行业资讯热点系统/crawler/_data/events_*.json"))[-1]
items = json.load(open(items_f, encoding="utf-8"))
evts = json.load(open(evts_f, encoding="utf-8"))

print("="*60)
print(f"📊 本次抓取: {len(items)} 条 items, {len(evts)} 个热点事件")
print("="*60)

print("\n🔥 Top 10 热点事件:")
for e in evts:
    print(f"  #{e['rank']}  score={e['hot_score']:.1f}  {e['source_count']}信源/{e['signal_count']}报道")
    print(f"       {e['title'][:70]}")
    print(f"       brands={e['brand_tags']}  type={e['event_type']}")

print("\n📈 Score 分布 (LLM 真实打分):")
buckets = {"90-100":0,"75-89":0,"60-74":0,"40-59":0,"0-39":0}
for it in items:
    s = it["score"]
    if s >= 90: buckets["90-100"] += 1
    elif s >= 75: buckets["75-89"] += 1
    elif s >= 60: buckets["60-74"] += 1
    elif s >= 40: buckets["40-59"] += 1
    else: buckets["0-39"] += 1
for k,v in buckets.items():
    bar = "█" * v
    print(f"  {k}: {v:>3}  {bar}")

print("\n📰 信源分布:")
from collections import Counter
for src, n in Counter(it["source_name"] for it in items).most_common():
    print(f"  {src:30s} {n:>3} 条")

print("\n✨ 处理方式:")
rule = sum(1 for it in items if "规则兜底" in it.get("reason",""))
llm_used = len(items) - rule
print(f"  LLM 真实处理: {llm_used} 条")
print(f"  规则兜底:     {rule} 条")

print("\n🏷️  Top 10 精选 (score >= 75):")
top = sorted([it for it in items if it["score"] >= 75], key=lambda x:-x["score"])[:10]
for it in top:
    print(f"  [{it['score']:>3}] {it['category']:10s} {','.join(it['brand_tags'][:2]):20s} {it['title'][:60]}")