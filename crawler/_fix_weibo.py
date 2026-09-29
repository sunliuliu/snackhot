import re
p = r'c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler\sources\weibo.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 找到所有 RawItem(...) 块，用更宽松的正则替换
new_block = '''raw = RawItem(
                            source_name=f"微博-{q['keyword']}",
                            title=self._extract_title(it["text"]),
                            url=it["link"],
                            author=it["userName"],
                            published_at=self._parse_time(it["timeText"]),
                            raw_content=json.dumps({
                                "text": it["text"],
                                "repost": it["repost"],
                                "comment": it["comment"],
                                "like": it["like"],
                                "heat_score": it["repost"]*3+it["comment"]*2+it["like"],
                                "keyword": q["keyword"],
                                "category": q["category"],
                            }, ensure_ascii=False),
                        )'''

# 匹配两个 RawItem 块（fetch 里的 + test 里的）
pattern = r'raw = RawItem\([^)]{5,200}\)'
# 先数一下匹配到几个
matches = re.findall(pattern, c, re.DOTALL)
print(f"匹配到 {len(matches)} 个 RawItem 块")

# 全部替换
c = re.sub(pattern, new_block, c, flags=re.DOTALL)

# 再检查有没有残留 tags= extra= content=
bad = [('tags=', 'content' in c and 'extra=' in c)]
if 'tags=' in c or 'extra=' in c or c.count('RawItem(') > 2:
    # 手动清残留
    c = re.sub(r'\s+tags=\[[^\]]*\],', '', c)
    c = re.sub(r'\s+extra=\{[^}]*\},?', '', c, flags=re.DOTALL)
    c = re.sub(r'\s+content=it\["text"\],', '', c)

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)
print("✅ weibo.py cleaned")
print(f"   RawItem blocks: {c.count('RawItem(')}")
print(f"   tags= residual: {'tags=' in c}")
print(f"   extra= residual: {'extra=' in c}")
