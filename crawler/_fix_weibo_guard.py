import re, json
from pathlib import Path

p = r'c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler\sources\weibo.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 1) 加 random hashlib import
c = c.replace(
    'import asyncio, re, json, sys, os',
    'import asyncio, re, json, sys, os, random, hashlib'
)

# 2) 在 USER_DATA_DIR 行之后插入防封配置块
anchor = 'USER_DATA_DIR = str(Path(__file__).resolve().parent.parent / ".weibo_profile")'
insert = anchor + r'''

# ============ 防封保险 ============
MIN_INTERVAL = 0.8       # 最小等待秒
MAX_INTERVAL = 1.6       # 最大等待秒
MAX_ROUNDS_PER_DAY = 4   # 每天最多爬几轮
_state_file = Path(__file__).resolve().parent.parent / ".weibo_state.json"

def _check_daily_limit() -> bool:
    """检查今日是否已达上限"""
    from datetime import datetime as _dt
    today = _dt.now().strftime("%Y-%m-%d")
    try:
        if _state_file.exists():
            st = json.loads(_state_file.read_text())
            if st.get("date") == today and st.get("rounds", 0) >= MAX_ROUNDS_PER_DAY:
                return False
    except:
        pass
    return True

def _record_round():
    """记录今日已爬一轮"""
    from datetime import datetime as _dt
    today = _dt.now().strftime("%Y-%m-%d")
    try:
        if _state_file.exists():
            st = json.loads(_state_file.read_text())
        else:
            st = {}
        if st.get("date") == today:
            st["rounds"] = st.get("rounds", 0) + 1
        else:
            st = {"date": today, "rounds": 1}
        _state_file.write_text(json.dumps(st))
    except:
        pass
'''
c = c.replace(anchor, insert)

# 3) 在 fetch() 里的 sleep 改成随机间隔
c = c.replace(
    'await page.wait_for_timeout(600)',
    'await page.wait_for_timeout(int(random.uniform(MIN_INTERVAL, MAX_INTERVAL) * 1000))'
)

# 4) 在 fetch() 方法开头加日上限检查
old_fetch_head = '    async def fetch(self) -> List[RawItem]:\n        """异步爬取所有关键词"""'
new_fetch_head = '''    async def fetch(self) -> List[RawItem]:
        """异步爬取所有关键词"""
        if not _check_daily_limit():
            print(f"  ⏰ 今日微博已达上限 ({MAX_ROUNDS_PER_DAY}轮)，跳过", flush=True)
            return []
        _record_round()'''
c = c.replace(old_fetch_head, new_fetch_head)

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)

print("✅ Done!")
print(f"   加了防封配置: MIN_INTERVAL={MIN_INTERVAL} MAX={MAX_INTERVAL} daily_cap={MAX_ROUNDS_PER_DAY}")
