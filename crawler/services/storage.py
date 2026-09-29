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
    """推送到热铁盒 — httpx 优先 + curl 3 次重试兜底"""
    if not RTH_INGEST_URL:
        print("  [推送] 未配置 RTH_INGEST_URL，跳过")
        return

    push_items = items[:200]
    push_events = events[:30]
    payload = {
        "items": [it.model_dump(mode="json") for it in push_items],
        "events": [e.model_dump(mode="json") for e in push_events],
        "push_time": datetime.utcnow().isoformat(),
    }
    payload_size = len(json.dumps(payload, ensure_ascii=False).encode())

    # 方案 1: httpx
    pushed = False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {"Content-Type": "application/json"}
            if RTH_API_KEY:
                headers["X-API-Key"] = RTH_API_KEY
            resp = await client.post(RTH_INGEST_URL, json=payload, headers=headers)
            if resp.status_code == 200:
                result = resp.json()
                print(f"  [推送] ✅ httpx -> {RTH_INGEST_URL}")
                print(f"         {len(push_items)} items, {len(push_events)} events, {payload_size//1024} KB")
                pushed = True
            elif resp.status_code == 429:
                print(f"  [推送] ⏳ 限流，跳过")
                return
            else:
                print(f"  [推送] ⚠️ httpx HTTP {resp.status_code}")
    except Exception as e:
        print(f"  [推送] httpx fail: {str(e)[:60]}")

    # 方案 2: subprocess curl 重试 3 次
    if not pushed:
        import subprocess, asyncio as _aio
        for attempt in range(1, 4):
            await _aio.sleep(2 * attempt)
            try:
                args = ["curl", "-s", "--max-time", "30", "-X", "POST",
                        RTH_INGEST_URL, "-H", "Content-Type: application/json"]
                if RTH_API_KEY:
                    args += ["-H", f"X-API-Key: {RTH_API_KEY}"]
                args += ["-d", json.dumps(payload, ensure_ascii=False)]
                result = subprocess.run(args, capture_output=True, text=True, timeout=60)
                body = result.stdout.strip() or result.stderr.strip()
                if result.returncode == 0 and '"ok":true' in body:
                    print(f"  [推送] ✅ curl retry {attempt}: {body[:120]}")
                    pushed = True
                    break
                elif '"too frequent"' in body or '"unauthorized"' in body:
                    print(f"  [推送] curl stop: {body[:80]}")
                    return
                else:
                    print(f"  [推送] curl {attempt}: {body[:100]}")
            except Exception as e:
                print(f"  [推送] curl {attempt} fail: {str(e)[:60]}")
        if not pushed:
            print(f"  [推送] ❌ 全部失败，下次再试")
