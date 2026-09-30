import math
import re
from typing import List, Dict
from collections import Counter
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import ProcessedItem, EventCluster
from config import SIMILARITY_THRESHOLD, MIN_SOURCES_FOR_HOT
from .scorer import compute_event_raw_score

def simple_tokenize(text):
    words = re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z]+", text)
    tokens = []
    for w in words:
        if len(w) >= 2:
            tokens.append(w)
    return tokens

def tokenize_cn(text):
    try:
        import jieba
        return [t for t in jieba.lcut(text) if len(t.strip()) > 1]
    except ImportError:
        return simple_tokenize(text)

def build_tfidf_vectors(items):
    n = len(items)
    docs_tokens = [tokenize_cn(f"{it.title} {it.summary}") for it in items]
    df = Counter()
    for tokens in docs_tokens:
        df.update(set(tokens))
    vocab = {w: i for i, w in enumerate(df.keys())}
    import numpy as np
    idf = {w: math.log(n / (df[w] + 1)) for w in vocab}
    vectors = []
    for tokens in docs_tokens:
        tf = Counter(tokens)
        vec = {}
        for w, cnt in tf.items():
            if w in idf:
                vec[w] = cnt * idf[w]
        vectors.append(vec)
    return vectors, vocab

def cosine(a, b):
    common = set(a.keys()) & set(b.keys())
    dot = sum(a[w] * b[w] for w in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def cluster_events(items):
    if not items or len(items) < 2:
        return []
    try:
        vectors, vocab = build_tfidf_vectors(items)
    except Exception as e:
        print(f"  聚类 TF-IDF 失败，跳过聚类: {e}")
        return []
    clusters = [[i] for i in range(len(items))]
    merged = True
    while merged:
        merged = False
        best_pair = None
        best_sim = 0.0
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                vi = vectors[clusters[i][0]]
                vj = vectors[clusters[j][0]]
                sim = cosine(vi, vj)
                if sim > best_sim:
                    best_sim = sim
                    best_pair = (i, j)
        if best_sim > SIMILARITY_THRESHOLD and best_pair:
            i, j = best_pair
            clusters[i].extend(clusters[j])
            clusters.pop(j)
            merged = True
    events = []
    import uuid
    from datetime import datetime
    for member_indices in clusters:
        members = [items[idx] for idx in member_indices]
        member_ids = [m.id for m in members]
        sources = set(m.source_name for m in members)
        titles = [m.title for m in members]
        category = Counter(m.category for m in members).most_common(1)[0][0]
        all_brands = set()
        for m in members:
            all_brands.update(m.brand_tags)
        best_title = max(titles, key=len)
        first_seen = min((m.discovered_at for m in members), default=datetime.utcnow())
        last_seen = max((m.discovered_at for m in members), default=datetime.utcnow())
        event = EventCluster(
            id=f"evt_{uuid.uuid4().hex[:12]}",
            title=best_title, summary="", category=category,
            brand_tags=list(all_brands),
            event_type=Counter(m.event_type for m in members).most_common(1)[0][0],
            member_ids=member_ids,
            source_count=len(sources),
            signal_count=len(members),
            first_seen_at=first_seen,
            last_seen_at=last_seen,
        )
        if event.source_count >= MIN_SOURCES_FOR_HOT or event.signal_count >= 3:
            event.hot_score = compute_event_raw_score(event, members)
            events.append(event)
    events.sort(key=lambda e: e.hot_score, reverse=True)
    for i, e in enumerate(events[:10], 1):
        e.rank = i
    return events[:10]
# ===== 零食连锁/食品品牌识别 (扩充自 2026-09-30) =====
BRAND_TAGS = {
    # 量贩零食 三巨头
    "鸣鸣很忙": ["量贩零食", "全国龙头"],
    "零食很忙": ["量贩零食", "全国龙头"],
    "赵一鸣":   ["量贩零食", "全国龙头"],
    "好想来":   ["量贩零食", "万辰集团"],
    "老婆大人": ["量贩零食", "万辰集团"],
    "来优品":   ["量贩零食", "万辰集团"],
    "零食有鸣": ["量贩零食", "区域龙头", "四川"],
    "糖巢":     ["量贩零食", "区域龙头", "福建"],
    "零食优选": ["量贩零食", "区域龙头", "湖南"],
    "爱零食":   ["量贩零食", "区域龙头", "湖南"],
    
    # 传统连锁
    "良品铺子": ["传统零食连锁", "上市公司"],
    "三只松鼠": ["传统零食连锁", "上市公司"],
    "来伊份":   ["传统零食连锁", "上市公司"],
    "薛记炒货": ["传统零食连锁", "高端炒货"],
    
    # 食品制造巨头
    "旺旺":     ["食品制造", "台湾"],
    "卫龙":     ["辣条", "食品制造"],
    "盐津铺子": ["食品制造", "上市公司"],
    "绝味":     ["卤味", "食品制造"],
    "洽洽":     ["炒货", "食品制造"],
    "亿滋":     ["食品制造", "外资"],
    "玛氏":     ["食品制造", "外资"],
    "雀巢":     ["食品制造", "外资"],
    "可口可乐": ["饮料", "外资"],
    "百事":     ["饮料", "外资"],
    "农夫山泉": ["饮料", "国货"],
    "元气森林": ["饮料", "国货", "气泡水"],
}
