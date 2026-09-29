"""主入口 —— 稳节奏串行调度版（带 flush 不缓冲）"""
import asyncio, sys, os, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print = lambda *a, **k: __builtins__['print'](*a, flush=True, **k) if isinstance(__builtins__, dict) else lambda *a, **k: sys.stdout.write(' '.join(map(str, a)) + '\n') or sys.stdout.flush()

from sources import ALL_CRAWLERS, ASYNC_CRAWLERS
from services.rate_limiter import RateLimiter
from services.deduper import dedupe_raw, dedupe_processed
from services.llm_processor import llm_process_batch
from services.hot_topic_engine import cluster_events
from services.storage import save_local, push_to_rth
from services.daily_report import generate_daily_report
from config import CACHE_DIR, DATA_DIR

async def main():
    # 强制不缓冲
    sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
    p = lambda *a, **k: (print(*a, flush=True, **k))

    p("=" * 60)
    p("  SnackHot Crawler  稳节奏串行版")
    p("=" * 60)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    limiter = RateLimiter()
    all_raw = []
    crawlers = list(ALL_CRAWLERS) + list(ASYNC_CRAWLERS)

    # ============ Step 1: 串行抓取 ============
    p(f"\n[1/6] 串行抓取（{len(crawlers)} 个 source）...")
    t_start = time.time()

    for crawler in crawlers:
        t0 = time.time()
        try:
            await limiter.wait(crawler.name)
            items = await crawler.fetch()
            dt = time.time() - t0
            p(f"  OK   {crawler.name}: {len(items)} 条  ({dt:.1f}s)")
            all_raw.extend(items)
            limiter.record_success(crawler.name)
        except Exception as e:
            dt = time.time() - t0
            p(f"  FAIL {crawler.name}: {str(e)[:50]} ({dt:.1f}s)")
            limiter.record_failure(crawler.name)

    p(f"\n  总计 {len(all_raw)} 条原始资讯, 总耗时 {time.time()-t_start:.0f}s")

    if not all_raw:
        p("没有抓到任何内容，退出。")
        return

    # ============ Step 2: 去重 ============
    p("\n[2/6] 标题去重...")
    all_raw = dedupe_raw(all_raw)
    p(f"  去重后 {len(all_raw)} 条")

    # ============ Step 3: LLM ============
    p("\n[3/6] LLM 摘要 + 打分 + 分类...")
    t_llm = time.time()
    processed = await llm_process_batch(all_raw)
    p(f"  LLM 完成 {len(processed)} 条, 耗时 {time.time()-t_llm:.0f}s")

    # ============ Step 4-6 ============
    p("\n[4/6] 二次去重...")
    processed = dedupe_processed(processed)
    p(f"  去重后 {len(processed)} 条")

    p("\n[5/6] 文本聚类生成热点事件...")
    hot_events = cluster_events(processed)
    p(f"  生成 {len(hot_events)} 个热点事件")

    p("\n[6/6] 生成每日早报...")
    daily = await generate_daily_report(hot_events, processed)

    p("\n[存储] 本地 JSON...")
    save_local(processed, hot_events, daily)

    if os.environ.get("RTH_INGEST_URL"):
        p("[存储] 推送热铁盒...")
        await push_to_rth(processed, hot_events)
    else:
        p("[存储] 跳过推送（未配置 RTH_INGEST_URL）")

    total_dt = time.time() - t_start
    p(f"\n✅ 完成！总耗时 {total_dt:.0f}s ({total_dt/60:.1f}min)")
    p(f"  items: {len(processed)}")
    p(f"  events: {len(hot_events)}")
    if hot_events:
        p("  Top 3:")
        for e in hot_events[:3]:
            p(f"    #{e.rank} {e.title[:50]} ({e.hot_score}分)")
    p(f"\n速率控制器状态:")
    p(limiter.status())

if __name__ == "__main__":
    asyncio.run(main())