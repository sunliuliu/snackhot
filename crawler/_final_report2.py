import json, sys, os
from collections import Counter

base = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统"

# 读最新 items
files = sorted([f for f in os.listdir(base + r"\crawler\_data") if f.startswith('items_') and f.endswith('.json')])
latest = files[-1]
with open(base + r"\crawler\_data" + os.sep + latest, encoding='utf-8') as f:
    items = json.load(f)

print('=' * 60)
print('  🔥 扩充信源后全链路结果')
print('=' * 60)
print()
print('Source 总数: 11 (之前 8, +3 国内媒体)')
print('微博关键词: 39 (之前 29, +10 新鲜零食)')
print('巨潮股票数: 19 (之前 8, +11)')
print('微博日限:   6 轮 (之前 4)')
print()
print(f'Total items: {len(items)} (之前 73, +334%)')
print()

# 来源分布
srcs = Counter()
for it in items:
    srcs[it.get('source_name','?')] += 1
print('来源分布:')
for s, c in srcs.most_common():
    print(f'  {s:35s} {c:3d} 条')

# 分数
scores = [it.get('score',0) for it in items]
scores.sort(reverse=True)
print()
print(f'LLM 分数: max={max(scores)}  avg={sum(scores)//len(scores)}  min={min(scores)}')
print('分布:')
ranges = {'90-100':0,'75-89':0,'60-74':0,'40-59':0,'0-39':0}
for s in scores:
    if s>=90: ranges['90-100']+=1
    elif s>=75: ranges['75-89']+=1
    elif s>=60: ranges['60-74']+=1
    elif s>=40: ranges['40-59']+=1
    else: ranges['0-39']+=1
for k, v in ranges.items():
    bar = '#' * v
    print(f'  {k:8s} {v:3d} {bar}')

# Top 10
print()
top = sorted(items, key=lambda x: x.get('score',0), reverse=True)[:10]
print('Top 10 最高相关度:')
for i, it in enumerate(top):
    brands = '/'.join((it.get('brand_tags') or [])[:3])
    print(f'  {i+1:2d}. {it.get("score",0):3d}分 [{it.get("category","?"):6s}] {brands:15s} {it.get("title","?")[:55]}')

# 品牌
brands = Counter()
for it in items:
    for b in (it.get('brand_tags') or []):
        brands[b] += 1
print()
print('Top 15 品牌提及:')
for b, n in brands.most_common(15):
    print(f'  {b:15s} {n:3d}次')

# 新鲜零食
fresh_kw = ['新鲜','鲜食','鲜货','锁鲜','短保','现做','鲜切','烘焙','金粒门','鲜目录','便利店','面包','鲜卤','果汁','钟薛高','冰淇淋','DQ','雪糕']
fresh_count = 0
fresh_items = []
for it in items:
    hay = ((it.get('title','') or '') + (it.get('summary','') or '') + ' ' + (' '.join(it.get('brand_tags') or []))).lower()
    if any(k.lower() in hay for k in fresh_kw) or it.get('category') == '新鲜零食':
        fresh_count += 1
        fresh_items.append(it)
print()
print(f'🥐 新鲜零食频道: {fresh_count} 条 (占比 {fresh_count*100//len(items)}%)')

print()
print('=' * 60)
print('  扩充前 vs 扩充后')
print('=' * 60)
print(f'  Source 数:  8  →  11      (+3)')
print(f'  微博关键词: 29  →  39     (+10)')
print(f'  巨潮股票:   8  →  19      (+11)')
print(f'  总条数:     73  →  {len(items):3d}  (+{len(items)-73})')
print(f'  倍数:       1x  →  {len(items)/73:.1f}x')
print('=' * 60)
