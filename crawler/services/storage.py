"""本地存储 + 热铁盒推送（WAF 绕过版 + ok 字段检查）

核心修复: Cloudflare WAF 会拦没有浏览器特征的 POST 请求 + 检查 ingest.ok 字段
  ✅ 完整浏览器 headers 伪装 (UA + Origin + Referer + Sec-* 系列)
  ✅ 检查返回 JSON 的 ok 字段 (ingest 限流时返回 ok:false + HTTP 200)
  ✅ payload 裁剪：只推 Top 200 精选 items
"""
import asyncio, json, os, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import ProcessedItem, EventCluster, DailyReport
from config import DATA_DIR, RTH_INGEST_URL, RTH_API_KEY

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "https://snackhot.rth3.xyz",
    "Referer": "https://snackhot.rth3.xyz/",
    "Content-Type": "application/json",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

def save_local(items, events, daily=None):
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

    try:
        import httpx
        headers = dict(BROWSER_HEADERS)
        if RTH_API_KEY:
            headers["X-API-Key"] = RTH_API_KEY

        print(f"  [推送] POST {RTH_INGEST_URL}  ({payload_size/1024:.1f} KB)")

        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.post(RTH_INGEST_URL, json=payload, headers=headers)

            if resp.status_code != 200:
                snippet = resp.text[:200] if resp.text else "(no body)"
                print(f"  [推送] ⚠️  HTTP {resp.status_code}: {snippet[:100]}")
                return

            # Cloudflare 拦截页检测
            content_type = resp.headers.get("content-type", "")
            if "html" in content_type.lower() and not resp.text.lstrip().startswith("{"):
                print(f"  [推送] ⚠️  Cloudflare WAF 拦截 (HTML, {len(resp.text)}B)")
                return

            result = resp.json()

            # ★ 关键: 检查 ok 字段！ingest 限流时返回 HTTP 200 但 ok:false
            if not result.get("ok"):
                err = result.get("error", "unknown error")
                print(f"  [推送] ⚠️  ingest 拒绝: {err}")
                return

            # 成功
            print(f"  [推送] ✅ 成功")
            print(f"         {len(push_items)} items, {len(push_events)} events, {payload_size/1024:.1f} KB")
            w = result.get('written', {})
            if w:
                if w.get('items_chunked') or w.get('events_chunked'):
                    print(f"         🎯 KV 分片触发! items={w.get('items_key','')} events={w.get('events_key','')}")
                else:
                    print(f"         items={w.get('items_key','')} events={w.get('events_key','')}")
    except ImportError:
        print("  [推送] httpx 未安装，跳过")
    except Exception as e:
        print(f"  [推送] ⚠️  失败: {str(e)[:80]}")