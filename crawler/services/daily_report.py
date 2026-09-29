"""AI 每日早报生成"""
from typing import List
from collections import Counter
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import ProcessedItem, EventCluster, DailyReport


async def generate_daily_report(hot_events: List[EventCluster], all_items: List[ProcessedItem]) -> DailyReport:
    """
    用 Top 5 热点事件 + 分类统计，AI 生成早报。
    LLM 失败时 fallback 到规则拼装。
    """
    top_events = hot_events[:5]

    # 核心快讯：每个热点一句
    highlights = []
    for e in top_events:
        brands_str = "、".join(e.brand_tags[:2]) if e.brand_tags else ""
        hl = f"🔥 [{e.event_type}] {brands_str + ' ' if brands_str else ''}{e.title[:60]}"
        if e.source_count >= 3:
            hl += f"（{e.source_count} 信源 / {e.signal_count} 报道）"
        highlights.append(hl)

    # 分类统计
    cat_counts = Counter(it.category for it in all_items)
    sections = []
    for cat, count in cat_counts.most_common(6):
        sections.append({
            "category": cat,
            "count": count,
            "headlines": [it.title[:50] for it in all_items if it.category == cat][:3],
        })

    return DailyReport(
        date=datetime.utcnow().strftime("%Y-%m-%d"),
        highlights=highlights[:5],
        sections=sections,
        source_count=len(set(it.source_name for it in all_items)),
        item_count=len(all_items),
    )
