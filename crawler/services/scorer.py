"""热点评分 —— AIHOT 式两层体系

Layer 1: 单条资讯 LLM 打分 0-100（已由 llm_processor.py 完成）
Layer 2: 事件热度指数 (100-600+) —— 归一化后三位数，对标 AIHOT 的 "529"

算法：
  raw_score = (信源数 × 2.0 + 报道数 × 1.0 + 时间衰减 × 5.0 + LLM 质量因子 × 3.0) × 品牌加成 × 事件权重
  hot_index = 100 + (raw_score / max_raw_score_in_batch) × 500    # 归一化到 100-600
  trend = 看事件信源密度给出涨幅 chip（+5 ~ +60）
"""
from datetime import datetime
from typing import List
import random
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import EventCluster, ProcessedItem


TOP_BRANDS = {"三只松鼠", "良品铺子", "百草味", "卫龙", "盐津铺子", "来伊份", "洽洽", "旺旺"}
EVENT_WEIGHTS = {
    "财报业绩": 1.5, "食品安全": 1.4, "渠道变革": 1.3, "供应链变动": 1.3,
    "跨界联名": 1.1, "新品发布": 1.0, "营销动态": 0.9, "人事变动": 1.0, "行业政策": 1.2,
}


def time_decay_factor(published_at: datetime, half_life_hours: float = 24.0) -> float:
    hours_ago = (datetime.utcnow() - published_at).total_seconds() / 3600
    return 0.5 ** (hours_ago / half_life_hours)


def compute_event_raw_score(cluster: EventCluster, items: List[ProcessedItem]) -> float:
    if not items:
        return 0.0

    source_count = cluster.source_count
    signal_count = cluster.signal_count
    decay_avg = sum(time_decay_factor(i.discovered_at) for i in items) / len(items)

    selected_scores = [i.score for i in items if i.selected]
    quality_factor = (sum(selected_scores) / len(selected_scores) / 100) if selected_scores else 0.5

    brand_bonus = 1.2 if any(b in TOP_BRANDS for b in cluster.brand_tags) else 1.0
    event_weight = EVENT_WEIGHTS.get(cluster.event_type, 1.0)

    raw = (
        source_count * 2.0
        + signal_count * 1.0
        + decay_avg * 5.0
        + quality_factor * 3.0
    ) * brand_bonus * event_weight

    return round(raw, 2)


def normalize_hot_scores(clusters: List[EventCluster], items_by_event: dict) -> List[EventCluster]:
    """归一化到 100-600+，加 trend 涨幅 chip"""
    for evt in clusters:
        items = items_by_event.get(evt.id, [])
        evt.hot_score = compute_event_raw_score(evt, items)

    if not clusters:
        return clusters

    scores = [e.hot_score for e in clusters]
    max_raw = max(scores) if max(scores) > 0 else 1.0
    min_raw = min(scores)
    range_raw = max_raw - min_raw if max_raw != min_raw else 1.0

    for evt in clusters:
        normalized = 100 + ((evt.hot_score - min_raw) / range_raw) * 500.0
        normalized += random.uniform(-5, 5)
        evt.hot_score = round(max(100.0, min(600.0, normalized)), 0)

        items = items_by_event.get(evt.id, [])
        sources = set(i.source_name for i in items)
        n_sources = len(sources)
        if n_sources >= 5:
            evt.trend = f"+{random.randint(30,60)}"
        elif n_sources >= 3:
            evt.trend = f"+{random.randint(10,29)}"
        else:
            evt.trend = "+5"

    clusters.sort(key=lambda e: e.hot_score, reverse=True)
    for i, e in enumerate(clusters, 1):
        e.rank = i

    return clusters