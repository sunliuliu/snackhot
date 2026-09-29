import re

BASE = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统"
p = BASE + r"\crawler\sources\weibo.py"
with open(p, encoding='utf-8') as f:
    c = f.read()

# 找 SEARCH_QUERIES 列表的最后一个元素并在后面加新鲜零食
# 先看原来的 FRESH_SNACK_KEYWORDS 块位置
fresh_block = '''
# ============ 新鲜零食赛道（注入 SEARCH_QUERIES） ============
FRESH_SNACK_QUERIES = [
    {"keyword": "金粒门 鲜货", "category": "新鲜零食"},
    {"keyword": "鲜目录 新鲜零食", "category": "新鲜零食"},
    {"keyword": "新鲜零食 赛道", "category": "新鲜零食"},
    {"keyword": "锁鲜装 零食", "category": "新鲜零食"},
    {"keyword": "短保零食 烘焙", "category": "新鲜零食"},
    {"keyword": "便利店 鲜食 面包", "category": "新鲜零食"},
    {"keyword": "现做卤味 鲜卤", "category": "新鲜零食"},
    {"keyword": "鲜切水果 零食", "category": "新鲜零食"},
    {"keyword": "量贩零食 鲜货", "category": "新鲜零食"},
    {"keyword": "零食集合店 新鲜", "category": "新鲜零食"},
]
'''

# 找到 SEARCH_QUERIES 最后一个 }] 的位置
# 原来的结尾应该是类似 ] 或者 ] 后面跟 class WeiboCrawler
# 策略：在 class WeiboCrawler 之前加 FRESH_SNACK_QUERIES 定义
# 然后把 SEARCH_QUERIES 扩展

# 1) 加 FRESH_SNACK_QUERIES
if 'FRESH_SNACK_QUERIES' not in c:
    c = c.replace('class WeiboCrawler', fresh_block + '\nclass WeiboCrawler')
    print("1. Added FRESH_SNACK_QUERIES list")
else:
    print("1. FRESH_SNACK_QUERIES already exists")

# 2) 在 SEARCH_QUERIES 后面用 + 扩展
# 找 SEARCH_QUERIES = [ ... ] 后面 class WeiboCrawler 的结构
# 实际文件是 SEARCH_QUERIES = [ ... L140: ] L142: class WeiboCrawler
# 所以把 ]\n\nclass WeiboCrawler 改成 ] + FRESH_SNACK_QUERIES\n\nclass WeiboCrawler
old_end = ']\n\nclass WeiboCrawler'
new_end = '] + FRESH_SNACK_QUERIES\n\nclass WeiboCrawler'

if '] + FRESH_SNACK_QUERIES' not in c:
    c = c.replace(old_end, new_end)
    print("2. Extended SEARCH_QUERIES + FRESH_SNACK_QUERIES")
else:
    print("2. SEARCH_QUERIES already extended")

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)

# 验证
with open(p, encoding='utf-8') as f:
    c2 = f.read()
print()
print("=== 验证 ===")
print("FRESH_SNACK_QUERIES 存在:", 'FRESH_SNACK_QUERIES' in c2)
print("SEARCH_QUERIES 已扩展:", '] + FRESH_SNACK_QUERIES' in c2)
