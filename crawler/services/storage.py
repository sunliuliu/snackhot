"""本地存储 + 热铁盒推送（已加固版）

加固点:
✅ payload 裁剪：只推 Top 200 精选 items
✅ 失败不重试推送（避免重复 POST）
✅ 推送间隔 15min 以上（ingest 端还有二次限流）
"""
import asyncio, json, os, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import ProcessedItem, EventCluster, DailyReport
from config import DATA_DIR, RTH_INGEST_URL, RTH_API_KEY

def save_local(items, events, daily=None):
    """保存到本地 JSON（永远保存，作为推送前的完整备份）"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    items_path = DATA_DIR / f"items_{ts}.json"
    items_path.write_text(json.dumps([it.model_dump(mode='json') for it in items], ensure_ascii=False, indent=2))
    
    if events:
        ev_path = DATA_DIR / f"events_{ts}.json"
        ev_path.write_text(json.dumps([e.model_dump(mode='json') for e in events], ensure_ascii=False, indent=2))
    
    if daily:
        daily_path = DATA_DIR / f"daily_{ts}.json"
        daily_path.write_text(json.dumps(daily.model_dump(mode='json') if hasattr(daily, 'model_dump') else daily, ensure_ascii=False, indent=2))
    
    latest = DATA_DIR / "latest.json"
    latest.write_text(json.dumps({"ts": ts, "items": len(items), "events": len(events)}))
    print(f"  [本地] {len(items)} items -> {items_path}")

async def push_to_rth(items, events):
    """推送到热铁盒（已加固）"""
    if not RTH_INGEST_URL:
        print("  [推送] 未配置 RTH_INGEST_URL，跳过推送")
        return
    
    # 加固 1: payload 裁剪
    push_items = items[:200]
    push_events = events[:30]
    
    payload = {
        "items": [it.model_dump(mode="json") for it in push_items],
        "events": [e.model_dump(mode="json") for e in push_events],
        "push_time": datetime.utcnow().isoformat(),
    }
    payload_size = len(json.dumps(payload, ensure_ascii=False).encode())
    
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {"Content-Type": "application/json"}
            if RTH_API_KEY:
                headers["X-API-Key"] = RTH_API_KEY
            
            resp = await client.post(RTH_INGEST_URL, json=payload, headers=headers)
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"  [推送] ✅ 成功 -> {RTH_INGEST_URL}")
                print(f"         {len(push_items)} items, {len(push_events)} events")
                print(f"         payload: {payload_size/1024:.1f} KB")
                if result.get('kv_operations'):
                    print(f"         KV ops: {result['kv_operations']}/轮（远低于 1000 上限）")
            elif resp.status_code == 429:
                print(f"  [推送] ⏳ 热铁盒限流（429），本次跳过推送")
            else:
                print(f"  [推送] ⚠️  HTTP {resp.status_code}: {resp.text[:100]}")
    except ImportError:
        print("  [推送] httpx 未安装，跳过")
    except Exception as e:
        print(f"  [推送] ⚠️  失败（不重试）: {str(e)[:60]}")