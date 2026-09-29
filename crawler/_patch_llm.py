p = r"c:\Users\user\.trae-cn\worktrees\零食行业资讯热点系统\crawler\services\llm_processor.py"
with open(p, encoding="utf-8") as f:
    c = f.read()

# 1) 在 config import 后加 Agnes 变量
c = c.replace(
    "from config import (\n    LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_TEMP, LLM_TIMEOUT,\n    FALLBACK_MODELS, FALLBACK_TO_RULE,\n    SUMMARY_MAX_WORDS, SCORE_THRESHOLD, BATCH_SIZE, MAX_RETRIES,\n)",
    "from config import (\n    LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_TEMP, LLM_TIMEOUT,\n    FALLBACK_MODELS, FALLBACK_TO_RULE,\n    SUMMARY_MAX_WORDS, SCORE_THRESHOLD, BATCH_SIZE, MAX_RETRIES,\n)\nimport os\nAGNES_BASE_URL = os.getenv('AGNES_BASE_URL', '')\nAGNES_API_KEY = os.getenv('AGNES_API_KEY', '')"
)

# 2) 在 _call_one_model 前插入 _resolve_provider
c = c.replace(
    "async def _call_one_model(batch: List[RawItem], model: str) -> Optional[List[dict]]:",
    '''def _resolve_provider(model: str) -> tuple:
    """根据模型名前缀路由到正确的供应商 (base_url, api_key)"""
    m = model.lower()
    if m.startswith("agnes-") and AGNES_BASE_URL and AGNES_API_KEY:
        return AGNES_BASE_URL, AGNES_API_KEY
    return LLM_BASE_URL, LLM_API_KEY

async def _call_one_model(batch: List[RawItem], model: str) -> Optional[List[dict]]:'''
)

# 3) 在 POST 前用动态 URL/Key
c = c.replace(
    """    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        resp = await client.post(
            f"{LLM_BASE_URL.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},""",
    """    base_url, api_key = _resolve_provider(model)
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        resp = await client.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},"""
)

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)

print("OK")
