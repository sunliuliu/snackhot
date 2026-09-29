"""LLM 处理 —— 多模型自动降级版

调用顺序:
  1. 主模型（LLM_MODEL）
  2. 备用模型列表（FALLBACK_MODELS）按序尝试
  3. 全挂 → 规则兜底

每次切换都打日志，谁能用谁上。
"""
from typing import List, Optional, Tuple
import json
import uuid
import time
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import RawItem, ProcessedItem
from config import (
    LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_TEMP, LLM_TIMEOUT,
    FALLBACK_MODELS, FALLBACK_TO_RULE,
    SUMMARY_MAX_WORDS, SCORE_THRESHOLD, BATCH_SIZE, MAX_RETRIES,
)
import os
AGNES_BASE_URL = os.getenv('AGNES_BASE_URL', '')
AGNES_API_KEY = os.getenv('AGNES_API_KEY', '')
SENSENOVA_BASE_URL = os.getenv('SENSENOVA_BASE_URL', '')
SENSENOVA_API_KEY = os.getenv('SENSENOVA_API_KEY', '')
from .classifier import classify

try:
    import httpx
except ImportError:
    httpx = None

# =====================================================
# Prompt
# =====================================================
SYSTEM_PROMPT = f"""你是「零食行业 AI 雷达」的核心分析引擎。
任务：对每条零食行业资讯进行摘要、分类、打分、精选决策。

评分标准（0-100）：
  90-100: 行业重大事件——头部零食品牌财报、食品安全、渠道革命
  75-89 : 行业重要新闻——新品发布、供应链变动、跨界联名、融资
  60-74 : 有参考价值——品牌营销、行业分析、门店动态
  40-59 : 普通信息——日常公关稿、转载类新闻
  0-39  : 低价值——水文、重复、无关零食

严格输出 JSON 数组，每个元素对应一条资讯：
  [{{"summary":"...","category":"...","brands":["..."],"event_type":"...","score":85,"reason":"..."}}]

字段：
  summary: 1-2 句中文摘要，≤ {SUMMARY_MAX_WORDS} 字
  category: 品类（坚果炒货/肉脯卤味/饼干糕点/糖果巧克力/休闲膨化/蜜饯果干/新鲜零食/冲调饮品/其他）
  brands: 零食品牌数组（如 ["三只松鼠","卫龙"]）
  event_type: 事件类型（财报业绩/渠道变革/新品发布/食品安全/供应链变动/跨界联名/营销动态/行业政策/人事变动/其他）
  score: 0-100 整数
  reason: 一句话推荐理由"""


def _build_items_text(raw_items: List[RawItem]) -> str:
    parts = []
    for i, item in enumerate(raw_items):
        parts.append(
            f"[{i}] 来源: {item.source_name}\n"
            f"标题: {item.title}\n"
            f"正文: {(item.raw_content or '')[:600]}"
        )
    return "\n\n".join(parts)


def _parse_llm_json(content: str, n: int) -> List[dict]:
    """容错 JSON 解析：处理 `json 包裹、空内容、尾部噪声"""
    text = content.strip()
    # 去掉 `json ... ` 包裹
    if text.startswith("`"):
        lines = text.split("\n")
        # 去掉第一行 `json
        if len(lines) > 1:
            text = "\n".join(lines[1:])
        # 去掉最后的 `
        text = text.rsplit("`", 1)[0]
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # 正则兜底找 [ ... ]
        import re
        m = re.search(r"\[.*\]", text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group())
            except Exception:
                return [{} for _ in range(n)]
        else:
            return [{} for _ in range(n)]

    if isinstance(data, dict):
        data = [data]
    # 保证返回 n 个
    while len(data) < n:
        data.append({})
    return data[:n]


# =====================================================
# 核心：调用 + 自动降级
# =====================================================
async def llm_process_batch(raw_items: List[RawItem]) -> List[ProcessedItem]:
    """批量入口：按主模型 → 备用列表 → 规则兜底 顺序尝试"""
    if not (LLM_BASE_URL and LLM_API_KEY and httpx):
        print(f"  [LLM] 未配置（需 .env 填 LLM_BASE_URL + LLM_API_KEY），规则兜底")
        return _fallback_process(raw_items)

    # 构造模型候选链：主模型 + 备用列表（去重保序）
    model_chain = [LLM_MODEL] + [m for m in FALLBACK_MODELS if m != LLM_MODEL]
    print(f"  [LLM] 候选模型链: {' → '.join(model_chain)}")

    n_batches = (len(raw_items) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"  [LLM] 共 {len(raw_items)} 条 / {n_batches} 批")

    processed: List[ProcessedItem] = []
    # 记录本轮最终用了哪个模型（第一 batch 成功的就是全局最优）
    active_model: Optional[str] = None

    for bi in range(n_batches):
        batch = raw_items[bi * BATCH_SIZE:(bi + 1) * BATCH_SIZE]
        result, used_model, err = await _try_models(batch, model_chain, active_model)
        if err and FALLBACK_TO_RULE:
            print(f"    batch {bi+1}/{n_batches} 全模型失败，规则兜底")
            processed.extend(_fallback_process(batch))
        elif err:
            raise err
        else:
            processed.extend(result)
            if active_model is None:
                active_model = used_model  # 锁定本次成功的模型，后续 batch 优先用它
            print(f"    batch {bi+1}/{n_batches} ✓ [{used_model}]")

    return processed


async def _try_models(
    batch: List[RawItem],
    model_chain: List[str],
    preferred_model: Optional[str] = None,
) -> Tuple[Optional[List[ProcessedItem]], Optional[str], Optional[Exception]]:
    """按优先级尝试模型，返回 (结果, 用了哪个模型, 全失败时的异常)"""

    # 优先用上次成功的模型
    ordered = [preferred_model] + [m for m in model_chain if m != preferred_model] if preferred_model else model_chain

    last_err = None
    for model in ordered:
        if not model:
            continue
        for attempt in range(MAX_RETRIES):
            try:
                results = await _call_one_model(batch, model)
                if results is not None:
                    return [_build_processed_item(raw, r) for raw, r in zip(batch, results)], model, None
            except Exception as e:
                last_err = e
                # 429 限流 / 401 Key 过期 → 直接放弃这个模型，重试没意义
                status = getattr(e, "status_code", None)
                msg = str(e)
                if status in (401, 403) or "rate_limit" in msg or "429" in msg:
                    break  # 跳出重试循环，换下一个模型
                # 其他错误（网络抖动）→ 再试一次
                await _sleep(0.5 * (attempt + 1))
    return None, None, last_err


def _resolve_provider(model: str) -> tuple:
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
    return LLM_BASE_URL, LLM_API_KEY

async def _call_one_model(batch: List[RawItem], model: str) -> Optional[List[dict]]:
    """调单个模型，解析 JSON。成功返回 list[dict]，失败抛异常"""
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_items_text(batch)},
        ],
        "max_tokens": 400,
        "temperature": LLM_TEMP,
    }
    # 某些模型不支持 response_format 或特殊参数
    if not ("kimi" in model.lower() or "sensechat" in model.lower()):
        body["response_format"] = {"type": "json_object"}

    base_url, api_key = _resolve_provider(model)
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        resp = await client.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=body,
        )
        if resp.status_code >= 400:
            # 把 status_code 挂到异常上方便上层判断
            exc = RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            exc.status_code = resp.status_code
            raise exc
        content = resp.json()["choices"][0]["message"]["content"]
        if not content or not content.strip():
            raise RuntimeError("empty response")
        return _parse_llm_json(content, len(batch))


def _build_processed_item(raw: RawItem, r: dict) -> ProcessedItem:
    """LLM 返回 + 规则补兜底"""
    category, brands, etype = classify(raw.title, raw.raw_content)
    llm_cat = r.get("category") or category
    llm_brands = r.get("brands") or brands
    llm_etype = r.get("event_type") or etype
    score_raw = r.get("score", 0) or 0
    # 兼容浮点（某些模型返回 7.5 而不是 75）
    try:
        score = int(float(score_raw))
    except (ValueError, TypeError):
        score = 0
    # 如果模型把评分标成 0-10 或 0-5 的小数，扩大到 0-100
    if 0 < score <= 10:
        score = int(score * 10)
    score = max(0, min(100, score))

    summary = (r.get("summary") or (raw.raw_content or raw.title))[:SUMMARY_MAX_WORDS]
    reason = r.get("reason") or ""

    return ProcessedItem(
        id=f"item_{uuid.uuid4().hex[:12]}",
        source_name=raw.source_name,
        title=raw.title,
        url=raw.url,
        published_at=raw.published_at,
        summary=summary,
        category=llm_cat,
        brand_tags=list(llm_brands) if llm_brands else brands,
        event_type=llm_etype,
        score=score if score > 0 else 50,
        selected=score >= SCORE_THRESHOLD,
        reason=reason,
    )


async def _sleep(seconds: float):
    import asyncio
    await asyncio.sleep(seconds)


def _fallback_process(raw_items: List[RawItem]) -> List[ProcessedItem]:
    """纯规则兜底：score=65 + 关键词分类"""
    processed = []
    for raw in raw_items:
        category, brands, etype = classify(raw.title, raw.raw_content)
        processed.append(ProcessedItem(
            id=f"item_{uuid.uuid4().hex[:12]}",
            source_name=raw.source_name,
            title=raw.title,
            url=raw.url,
            published_at=raw.published_at,
            summary=(raw.raw_content or raw.title)[:SUMMARY_MAX_WORDS],
            category=category,
            brand_tags=brands,
            event_type=etype,
            score=65,
            selected=True,
            reason="规则兜底（未启用 LLM）",
        ))
    return processed