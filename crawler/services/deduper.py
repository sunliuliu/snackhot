"""基于标题相似度的去重"""
from difflib import SequenceMatcher
from typing import List
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import RawItem, ProcessedItem


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def dedupe_raw(items: List[RawItem], threshold: float = 0.85) -> List[RawItem]:
    """对 RawItem 按标题相似度去重，保留先抓到的"""
    seen_titles: List[str] = []
    result: List[RawItem] = []

    for item in items:
        is_dup = False
        for seen in seen_titles:
            if title_similarity(item.title, seen) > threshold:
                is_dup = True
                break
        if not is_dup:
            seen_titles.append(item.title)
            result.append(item)

    removed = len(items) - len(result)
    if removed:
        print(f"  去重移除 {removed} 条重复报道")
    return result


def dedupe_processed(items: List[ProcessedItem], threshold: float = 0.8) -> List[ProcessedItem]:
    """对 ProcessedItem 做二次去重（已在 Raw 层去过，但不同信源可能抓到同一事件）"""
    seen_titles: List[str] = []
    result: List[ProcessedItem] = []

    for item in items:
        is_dup = False
        for seen in seen_titles:
            if title_similarity(item.title, seen) > threshold:
                is_dup = True
                break
        if not is_dup:
            seen_titles.append(item.title)
            result.append(item)

    removed = len(items) - len(result)
    if removed:
        print(f"  二次去重移除 {removed} 条")
    return result
