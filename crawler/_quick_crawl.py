import asyncio, sys, json
sys.path.insert(0, '.')
from collections import Counter
from pathlib import Path

from sources import ALL_CRAWLERS, ASYNC_CRAWLERS

async def main():
    print("=" * 60)
    print("  SnackHot Full Crawl Test (skip LLM)")
    print("=" * 60)

    tasks = [c.fetch() for c in ALL_CRAWLERS] + [c.fetch() for c in ASYNC_CRAWLERS]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total = 0
    all_items = []
    all_crawlers = list(ALL_CRAWLERS) + list(ASYNC_CRAWLERS)
    for crawler, res in zip(all_crawlers, results):
        if isinstance(res, Exception):
            print(f"  FAIL {crawler.name}: {str(res)[:60]}")
        else:
            print(f"  OK   {crawler.name}: {len(res)} items")
            total += len(res)
            all_items.extend(res)

    print(f"\n  TOTAL: {total}")
    sources = Counter()
    for it in all_items:
        src = it.source_name.split('-')[0]
        sources[src] += 1
    print("  Source breakdown:")
    for src, cnt in sources.most_common():
        print(f"    {src}: {cnt}")

    out = Path("../../data/raw_items.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([
        {"source": it.source_name, "title": it.title, "url": it.url, "preview": it.raw_content[:200]}
        for it in all_items
    ], ensure_ascii=False, indent=2))
    print(f"\n  Saved to {out}")

asyncio.run(main())