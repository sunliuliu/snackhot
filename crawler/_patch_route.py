import os, sys
p = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler\services\llm_processor.py"
with open(p, encoding="utf-8") as f:
    c = f.read()

# 1) 加 SENSENOVA 变量读取（在 AGNES 下面）
c = c.replace(
    "AGNES_BASE_URL = os.getenv('AGNES_BASE_URL', '')\nAGNES_API_KEY = os.getenv('AGNES_API_KEY', '')",
    "AGNES_BASE_URL = os.getenv('AGNES_BASE_URL', '')\nAGNES_API_KEY = os.getenv('AGNES_API_KEY', '')\nSENSENOVA_BASE_URL = os.getenv('SENSENOVA_BASE_URL', '')\nSENSENOVA_API_KEY = os.getenv('SENSENOVA_API_KEY', '')"
)

# 2) 升级路由函数：三个供应商全覆盖
old = '''def _resolve_provider(model: str) -> tuple:
    """根据模型名前缀路由到正确的供应商 (base_url, api_key)"""
    m = model.lower()
    if m.startswith("agnes-") and AGNES_BASE_URL and AGNES_API_KEY:
        return AGNES_BASE_URL, AGNES_API_KEY
    return LLM_BASE_URL, LLM_API_KEY'''

new = '''def _resolve_provider(model: str) -> tuple:
    """根据模型名前缀路由到正确的供应商 (base_url, api_key)
    
    路由表:
      agnes-*        -> Agnes AI (免费 flash 系列)
      sensenova-*    -> SenseNova (备用)
      deepseek-*     -> 当前主供应商 Agnes 也支持 deepseek 系模型名
      其他           -> LLM_BASE_URL (默认)
    """
    m = model.lower()
    if m.startswith("agnes-") and AGNES_BASE_URL and AGNES_API_KEY:
        return AGNES_BASE_URL, AGNES_API_KEY
    if m.startswith("sensenova-") and SENSENOVA_BASE_URL and SENSENOVA_API_KEY:
        return SENSENOVA_BASE_URL, SENSENOVA_API_KEY
    return LLM_BASE_URL, LLM_API_KEY'''

c = c.replace(old, new)

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)
print("OK")
